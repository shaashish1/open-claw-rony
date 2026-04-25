#!/bin/bash
sudo python3 /tmp/patch_jira_v2.py
sudo systemctl restart itgyani-dashboard
sleep 7
echo -n "jira-sprint HTTP: "
curl -sw "%{http_code}" http://127.0.0.1:8002/api/ops/jira-sprint -o /tmp/jira_out.json
echo ""
cat /tmp/jira_out.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f'total={d[\"total\"]}, done={d[\"done\"]}, in_progress={d[\"in_progress\"]}')
for i in d['issues'][:8]:
    print(f'  {i[\"key\"]}: {i[\"summary\"][:45]} [{i[\"status\"]}]')
"
