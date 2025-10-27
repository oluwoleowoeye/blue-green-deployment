# Blue-Green Node.js Deployment with Nginx

This project demonstrates a blue-green deployment strategy for Node.js services using Docker Compose and Nginx with automatic failover.

## Architecture

- **Nginx**: Load balancer with automatic failover (port 8080)
- **Blue Service**: Primary service instance (direct port 8081)
- **Green Service**: Backup service instance (direct port 8082)

## Features

- ✅ Zero-downtime failover between blue and green instances
- ✅ Automatic retry within the same client request
- ✅ Fast failure detection (2s timeouts)
- ✅ HTTP 5xx and timeout retry logic
- ✅ Preserved upstream headers (X-App-Pool, X-Release-Id)
- ✅ Health checks and monitoring
- ✅ Chaos testing endpoints for simulation

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone https://github.com/oluwoleowoeye/blue-green-deployment.git
   cd blue-green-nodejs
   cp .env.example .env
   # Edit .env if needed
