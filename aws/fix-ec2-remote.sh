#!/bin/bash
set -x
exec >> /var/log/powerguard-fix.log 2>&1

echo "=== PowerGuard remote fix $(date) ==="

docker stop powerguard 2>/dev/null || true
docker rm powerguard 2>/dev/null || true
systemctl stop docker 2>/dev/null || true

dnf install -y python3 python3-pip git

if ! swapon --show | grep -q /swapfile; then
  fallocate -l 2G /swapfile 2>/dev/null || dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
fi

mkdir -p /opt/powerguard
cd /opt/powerguard
rm -rf app
git clone https://github.com/ldrago8/powerguard-theft-detection.git app
cd app

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

export DEPLOYMENT_ENV=cloud
export POWERGUARD_STORAGE=/tmp/powerguard-storage
export PYTHONUTF8=1

if [ ! -f ml/artifacts/theft_detection_model.pkl ]; then
  python3 ml/train_model.py
fi

BUCKET="powerguard-theft-detection-powerguardbucket-d5y28rcim6hw"
aws s3 cp data/electricity_consumption.csv "s3://${BUCKET}/data/electricity_consumption.csv" || true
aws s3 cp ml/artifacts/theft_detection_model.pkl "s3://${BUCKET}/ml/theft_detection_model.pkl" 2>/dev/null || true

cat > /etc/systemd/system/powerguard.service << EOF
[Unit]
Description=PowerGuard Electricity Theft Detection
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/powerguard/app
Environment=DEPLOYMENT_ENV=cloud
Environment=POWERGUARD_STORAGE=/tmp/powerguard-storage
Environment=PYTHONUTF8=1
Environment=AWS_S3_BUCKET=${BUCKET}
ExecStart=/usr/bin/python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 80
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable powerguard
systemctl restart powerguard
sleep 5
systemctl status powerguard --no-pager
curl -s http://127.0.0.1/api/health || true
echo "=== Fix complete ==="
