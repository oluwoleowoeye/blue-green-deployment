#!/usr/bin/env python3
import os
import time
import requests
import re
from collections import deque
from datetime import datetime

# Configuration from environment
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
ERROR_RATE_THRESHOLD = float(os.getenv('ERROR_RATE_THRESHOLD', '2.0'))
WINDOW_SIZE = int(os.getenv('WINDOW_SIZE', '200'))
ALERT_COOLDOWN_SEC = int(os.getenv('ALERT_COOLDOWN_SEC', '300'))

# State tracking
last_failover_alert_time = 0
last_error_alert_time = 0
current_pool = os.getenv('ACTIVE_POOL', 'blue')
request_window = deque(maxlen=WINDOW_SIZE)  # Rolling 200-request window
error_alert_active = False

def send_slack_alert(message, alert_type="failover"):
    """Send alert to Slack with rate-limiting"""
    global last_failover_alert_time, last_error_alert_time
    
    current_time = time.time()
    
    # Enforce cooldowns
    if alert_type == "failover":
        if current_time - last_failover_alert_time < ALERT_COOLDOWN_SEC:
            return False
    elif alert_type == "error":
        if current_time - last_error_alert_time < ALERT_COOLDOWN_SEC:
            return False
    
    if not SLACK_WEBHOOK_URL:
        return False
        
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        full_message = f"{message}\n*Time:* {timestamp}"
        payload = {"text": full_message}
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            if alert_type == "failover":
                last_failover_alert_time = current_time
            elif alert_type == "error":
                last_error_alert_time = current_time
            print(f"✅ Alert sent: {message}")
            return True
    except Exception as e:
        print(f"❌ Alert failed: {e}")
    return False

def parse_nginx_log(line):
    """Parse nginx log for pool, upstream status, and other fields"""
    pattern = r'"([^"]*)"\s+"([^"]*)"\s+"([^"]*)"\s+"([^"]*)"\s+"([^"]*)"$'
    match = re.search(pattern, line)
    
    if match:
        upstream_addr = match.group(1)
        upstream_status = match.group(2)
        x_app_pool = match.group(3)
        x_release_id = match.group(4)
        x_version = match.group(5)
        
        # Determine pool
        pool = None
        if 'blue' in x_app_pool.lower():
            pool = 'blue'
        elif 'green' in x_app_pool.lower():
            pool = 'green'
        
        # Parse upstream status
        upstream_status_code = int(upstream_status) if upstream_status.isdigit() else None
        
        return pool, upstream_status_code, upstream_addr, x_release_id, x_version
    
    return None, None, '', '', ''

def monitor_logs():
    """Main function that meets all requirements"""
    global current_pool, error_alert_active
    
    print("🚀 Alert Watcher Service Started")
    print(f"Monitoring: {WINDOW_SIZE}-request window, {ERROR_RATE_THRESHOLD}% error threshold")
    
    while True:
        try:
            with open('/var/log/nginx/access.log', 'r') as f:
                # Real-time tailing
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        # Parse pool and upstream status fields
                        pool, upstream_status, upstream_addr, release_id, version = parse_nginx_log(line)
                        
                        # Detect pool flips compared to last seen pool
                        if pool and pool != current_pool:
                            print(f"🔀 Pool flip: {current_pool} → {pool}")
                            message = f"🚨 Failover: {current_pool} → {pool}"
                            if upstream_addr and upstream_addr != "-":
                                message += f"\n*Upstream:* {upstream_addr}"
                            if release_id and release_id != "-":
                                message += f"\n*Release:* {release_id}"
                            
                            # Send on first failover event after chaos injection
                            if send_slack_alert(message, "failover"):
                                current_pool = pool
                        
                        # Maintain rolling error-rate window for upstream 5xx errors
                        if upstream_status:
                            if upstream_status >= 500:
                                request_window.append(1)  # 5xx error
                            elif 200 <= upstream_status < 500:
                                request_window.append(0)  # Success
                        
                        # Check for error-rate threshold breach (>2% over last 200 requests)
                        if len(request_window) >= WINDOW_SIZE:
                            errors = sum(request_window)
                            error_rate = (errors / WINDOW_SIZE) * 100
                            
                            # Elevated upstream 5xx error rates over sliding window
                            if error_rate > ERROR_RATE_THRESHOLD and not error_alert_active:
                                message = f"⚠️ High Error Rate: {error_rate:.2f}% ({errors}/{WINDOW_SIZE} upstream 5xx errors)"
                                if send_slack_alert(message, "error"):
                                    error_alert_active = True
                                    print(f"🚨 Error-rate alert triggered: {error_rate:.2f}%")
                            
                            elif error_rate <= ERROR_RATE_THRESHOLD and error_alert_active:
                                message = f"✅ Error Rate Normal: {error_rate:.2f}%"
                                if send_slack_alert(message, "error"):
                                    error_alert_active = False
                    
                    else:
                        time.sleep(0.1)
                        
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    monitor_logs()
