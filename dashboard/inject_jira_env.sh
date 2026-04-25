#!/bin/bash
TOKEN="ATATT3xFfGF0GJ97pfigXVh7SDeOMP2c4ne74qmxi0n1t3Y6L93c9iNCim18ghom76w2g81qdDUvszrmqikeW5mlx_gJyd4zKklPfT_qgp6JRsz-FhCNsLP-knxeKBkTrSoSRGONbgPexGeWtwowxaADczDBtOQqx1xlInRqNQxcKg4ApeqYsQE=0C283DB8"

# Add JIRA env vars to service if not already there
if ! grep -q JIRA_TOKEN /etc/systemd/system/itgyani-dashboard.service; then
    sed -i "/\[Service\]/a Environment=\"JIRA_TOKEN=${TOKEN}\"\nEnvironment=\"JIRA_EMAIL=ashish@itgyani.com\"\nEnvironment=\"JIRA_DOMAIN=itgyani.atlassian.net\"" /etc/systemd/system/itgyani-dashboard.service
    echo "Jira env injected"
else
    echo "Already has JIRA_TOKEN"
fi

systemctl daemon-reload
systemctl restart itgyani-dashboard
sleep 6

echo -n "api/ops/status: "
curl -sw "%{http_code}" http://127.0.0.1:8002/api/ops/status -o /dev/null
echo ""

echo -n "api/ops/jira-sprint: "
curl -sw "%{http_code}" http://127.0.0.1:8002/api/ops/jira-sprint | head -c 200
echo ""
