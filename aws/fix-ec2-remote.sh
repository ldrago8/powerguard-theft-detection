#!/bin/bash
# Emergency fix: restart Docker container with writable storage env vars
set -x
systemctl stop powerguard 2>/dev/null || true
systemctl disable powerguard 2>/dev/null || true
systemctl start docker
docker stop powerguard 2>/dev/null || true
docker rm powerguard 2>/dev/null || true
docker run -d \
  --name powerguard \
  --restart unless-stopped \
  -p 80:7860 \
  -e DEPLOYMENT_ENV=cloud \
  -e POWERGUARD_STORAGE=/tmp/powerguard-storage \
  -e PORT=7860 \
  powerguard:latest
sleep 10
curl -s http://127.0.0.1/api/health
