#!/bin/bash
JIRA_TOKEN="ATATT3xFfGF0GJ97pfigXVh7SDeOMP2c4ne74qmxi0n1t3Y6L93c9iNCim18ghom76w2g81qdDUvszrmqikeW5mlx_gJyd4zKklPfT_qgp6JRsz-FhCNsLP-knxeKBkTrSoSRGONbgPexGeWtwowxaADczDBtOQqx1xlInRqNQxcKg4ApeqYsQE=0C283DB8"
JIRA_EMAIL="ashish@itgyani.com"

echo "=== ALL PROJECTS ==="
curl -s "https://itgyani.atlassian.net/rest/api/3/project" \
  -u "$JIRA_EMAIL:$JIRA_TOKEN" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for p in d:
    print(p.get('key',''),'|',p.get('name',''),'|',p.get('id',''))
"

echo ""
echo "=== BOARD 7 ISSUES (all) ==="
curl -s "https://itgyani.atlassian.net/rest/agile/1.0/board/7/issue?maxResults=100&fields=summary,status,assignee,priority,issuetype" \
  -u "$JIRA_EMAIL:$JIRA_TOKEN" | python3 -c "
import json,sys
d=json.load(sys.stdin)
issues=d.get('issues',[])
print('Total:',len(issues))
status_counts={}
for i in issues:
    s=i['fields']['status']['name']
    status_counts[s]=status_counts.get(s,0)+1
print('Status breakdown:',json.dumps(status_counts))
for i in issues[:50]:
    key=i['key']
    status=i['fields']['status']['name']
    cat=i['fields']['status']['statusCategory']['key']
    assignee=i['fields'].get('assignee') or {}
    aname=assignee.get('displayName','-')
    summ=i['fields']['summary'][:55]
    print(key,'|',status,'|',aname,'|',summ)
"
