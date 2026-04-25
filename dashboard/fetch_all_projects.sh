#!/bin/bash
JIRA_TOKEN="ATATT3xFfGF0GJ97pfigXVh7SDeOMP2c4ne74qmxi0n1t3Y6L93c9iNCim18ghom76w2g81qdDUvszrmqikeW5mlx_gJyd4zKklPfT_qgp6JRsz-FhCNsLP-knxeKBkTrSoSRGONbgPexGeWtwowxaADczDBtOQqx1xlInRqNQxcKg4ApeqYsQE=0C283DB8"
JIRA_EMAIL="ashish@itgyani.com"

for PROJECT in CG TEF YUKTI KO QPF SF SUP; do
  echo "=== $PROJECT ==="
  curl -s "https://itgyani.atlassian.net/rest/api/3/search?jql=project=$PROJECT&maxResults=30&fields=summary,status,assignee,priority" \
    -u "$JIRA_EMAIL:$JIRA_TOKEN" | python3 -c "
import json,sys
d=json.load(sys.stdin)
issues=d.get('issues',[])
print('Total:',len(issues))
for i in issues[:15]:
    key=i['key']
    s=i['fields']['status']['name']
    summ=i['fields']['summary'][:50]
    print(key,'|',s,'|',summ)
" 2>/dev/null
  echo ""
done
