#!/bin/bash
JIRA_TOKEN="ATATT3xFfGF0GJ97pfigXVh7SDeOMP2c4ne74qmxi0n1t3Y6L93c9iNCim18ghom76w2g81qdDUvszrmqikeW5mlx_gJyd4zKklPfT_qgp6JRsz-FhCNsLP-knxeKBkTrSoSRGONbgPexGeWtwowxaADczDBtOQqx1xlInRqNQxcKg4ApeqYsQE=0C283DB8"
JIRA_EMAIL="ashish@itgyani.com"
BASE="https://itgyani.atlassian.net/rest/api/3"

curl -s -X POST "$BASE/search/jql" \
  -u "$JIRA_EMAIL:$JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jql": "project in (IT,CG,TEF,YUKTI,KO,QPF,SF,SUP) ORDER BY project ASC",
    "maxResults": 200,
    "fields": ["summary","status","assignee","priority","issuetype","project"]
  }' | python3 -c "
import json,sys
d=json.load(sys.stdin)
if 'errorMessages' in d:
    print('ERROR:', d['errorMessages'])
    sys.exit(1)
issues=d.get('issues',[])
print('TOTAL:', len(issues))
by_project={}
for i in issues:
    proj=i['fields']['project']['key']
    pname=i['fields']['project']['name']
    s=i['fields']['status']['statusCategory']['key']
    sname=i['fields']['status']['name']
    by_project.setdefault(proj,{'name':pname,'issues':[]})['issues'].append({
        'key':i['key'],'status':sname,'cat':s,'summary':i['fields']['summary']
    })
for proj,data in sorted(by_project.items()):
    items=data['issues']
    done=sum(1 for x in items if x['cat']=='done')
    prog=sum(1 for x in items if x['cat']=='indeterminate')
    todo=sum(1 for x in items if x['cat']=='new')
    print(f'PROJECT:{proj}|{data[\"name\"]}|total={len(items)}|done={done}|prog={prog}|todo={todo}')
    for x in items:
        print(f'  ISSUE:{x[\"key\"]}|{x[\"status\"]}|{x[\"cat\"]}|{x[\"summary\"]}')
" 2>/dev/null
