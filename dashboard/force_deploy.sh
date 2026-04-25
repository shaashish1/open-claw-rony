#!/bin/bash
cd /tmp/rony-deploy
git fetch origin
git reset --hard origin/main
cp dashboard/backend/*.py /opt/itgyani-dashboard/
cp dashboard/frontend/ops.html /opt/itgyani-dashboard/frontend/ops.html
systemctl restart itgyani-dashboard
sleep 8
echo -n "jira-sprint HTTP: "
curl -sw "%{http_code}" http://127.0.0.1:8002/api/ops/jira-sprint -o /tmp/jira_test.json
echo ""
python3 -c "
import json
d=json.load(open('/tmp/jira_test.json'))
print(f'total={d[\"total\"]}, done={d[\"done\"]}, in_progress={d[\"in_progress\"]}')
for i in d['issues'][:5]:
    print(f'  {i[\"key\"]}: {i[\"summary\"][:40]} [{i[\"status\"]}]')
"
