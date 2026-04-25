#!/bin/bash
JIRA_TOKEN="ATATT3xFfGF0GJ97pfigXVh7SDeOMP2c4ne74qmxi0n1t3Y6L93c9iNCim18ghom76w2g81qdDUvszrmqikeW5mlx_gJyd4zKklPfT_qgp6JRsz-FhCNsLP-knxeKBkTrSoSRGONbgPexGeWtwowxaADczDBtOQqx1xlInRqNQxcKg4ApeqYsQE=0C283DB8"
JIRA_EMAIL="ashish@itgyani.com"
BASE="https://itgyani.atlassian.net/rest/api/3"

for PROJ in TEF YUKTI QPF SF SUP; do
  echo "=== $PROJ ==="
  curl -s -X POST "$BASE/search/jql" \
    -u "$JIRA_EMAIL:$JIRA_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"jql\":\"project=$PROJ ORDER BY created ASC\",\"maxResults\":50,\"fields\":[\"summary\",\"status\",\"project\"]}" \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
issues=d.get('issues',[])
done=sum(1 for i in issues if i['fields']['status']['statusCategory']['key']=='done')
prog=sum(1 for i in issues if i['fields']['status']['statusCategory']['key']=='indeterminate')
print(f'total={len(issues)} done={done} prog={prog} todo={len(issues)-done-prog}')
for i in issues[:8]:
    print(i['key'],'|',i['fields']['status']['name'],'|',i['fields']['summary'][:55])
" 2>/dev/null
  echo ""
done
