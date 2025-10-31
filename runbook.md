# Blue-Green Deployment Runbook

## Alert Meanings & Operator Actions

**Failover detected** (Traffic switched between blue/green pools) → Check health of primary container: `docker-compose ps app_blue app_green && docker-compose logs [failed-pool] --tail=10`

**Error-rate high** (>2% 5xx errors over last 200 requests) → Inspect upstream logs, possibly toggle pools: `docker exec nginx-1 tail -20 access.log | grep " 50"` and `docker-compose stop app_blue` (or `app_green`)

**Recovery** (Primary is serving traffic again) → Verify normal operation: `curl http://localhost:8080/version`

**Suppress alerts during planned toggles** → Maintenance mode: `docker-compose stop watcher` (disable), `docker-compose start watcher` (enable)
