# Blue-Green Deployment with Nginx (operational visibility and actionable alerts)

This project demonstrates a blue-green deployment strategy for Node.js services using Docker Compose and Nginx with automatic failover.

## Architecture

- **Nginx**: Load balancer with automatic failover (port 8080)
- **Blue Service**: Primary service instance (direct port 8081)
- **Green Service**: Backup service instance (direct port 8082)
- **Watcher Service**: Monitors logs and sends Slack alerts

## Features

- ✅ Zero-downtime failover between blue and green instances
- ✅ Automatic retry within the same client request
- ✅ Fast failure detection (2s timeouts)
- ✅ HTTP 5xx and timeout retry logic
- ✅ Preserved upstream headers (X-App-Pool, X-Release-Id)
- ✅ Health checks and monitoring
- ✅ Chaos testing endpoints for simulation
- ✅ Real-time Slack alerts for failovers and error rates
  
## Quick Start

1. **Clone and setup**:
   ```bash
   git clone https://github.com/oluwoleowoeye/blue-green-deployment.git
   cd blue-green-deployment
   cp .env.example .env
   #  Edit .env with your SLACK_WEBHOOK_URL
2. **Start the services**:
   ```bash
   docker-compose up -d
2. **Verify deplyment**:
   ```bash
   curl http://localhost:8080/version

## Chaos Testing 

**Test Failover (Blue → Green)**: 
# Stop Blue service - should trigger automatic failover to Green 
```bash 
docker-compose stop app_blue
curl http://localhost:8080/version  # Should show "pool":"green"

# Restore Blue
```bash 
docker-compose start app_blue 

**Test Error Rate Alerts**: 
# Generate 5xx errors to trigger error-rate alert
```bash 
docker-compose stop app_blue
for i in {1..10}; do curl http://localhost:8081/version; sleep 0.1; done
docker-compose start app_blue

## Monitoring and Testing
# Watcher alerts and activity: 
```bash 
docker-compose logs watcher --tail=20 --follow

# Nginx access logs: 
```bash 
docker-compose logs nginx --tail=10

# Application logs: 
```bash 
docker-compose logs app_blue --tail=5
docker-compose logs app_green --tail=5

## Verify Slack Alerts:
Ensure SLACK_WEBHOOK_URL is set in .env

Run chaos tests above

Check your Slack channel for:

🚨 Failover alerts (blue → green or green → blue)

⚠️ High Error Rate alerts (>2% 5xx errors)

## Screenshots:

# Slack alerts for failovers and error rates
 `![Blue to Green Failover](/blue-green-deployment/blue to green.png)`
