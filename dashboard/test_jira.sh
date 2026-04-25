#!/bin/bash
TOKEN=$(grep JIRA_TOKEN /etc/environment | cut -d= -f2-)
EMAIL="ashish@itgyani.com"
DOMAIN="itgyani.atlassian.net"
CREDS=$(echo -n "$EMAIL:$TOKEN" | base64 -w0)

echo "=== Testing Jira Agile API ==="
echo -n "Board 7 sprints: "
curl -sw " HTTP_%{http_code}" "https://$DOMAIN/rest/agile/1.0/board/7/sprint?state=active,future&maxResults=5" \
  -H "Authorization: Basic $CREDS" -H "Accept: application/json" -o /tmp/jira_sprints.json
echo ""
cat /tmp/jira_sprints.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d,indent=2)[:600])"

echo ""
echo -n "Board 7 issues: "
curl -sw " HTTP_%{http_code}" "https://$DOMAIN/rest/agile/1.0/board/7/issue?maxResults=10" \
  -H "Authorization: Basic $CREDS" -H "Accept: application/json" -o /tmp/jira_issues.json
echo ""
cat /tmp/jira_issues.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d,indent=2)[:400])"

echo ""
echo -n "Rest v2 search: "
curl -sw " HTTP_%{http_code}" "https://$DOMAIN/rest/api/2/search?jql=project=IT+ORDER+BY+created+DESC&maxResults=5&fields=summary,status" \
  -H "Authorization: Basic $CREDS" -H "Accept: application/json" -o /tmp/jira_search.json
echo ""
cat /tmp/jira_search.json | python3 -c "import json,sys; d=json.load(sys.stdin); [print(f'  {i[\"key\"]}: {i[\"fields\"][\"summary\"][:40]} [{i[\"fields\"][\"status\"][\"name\"]}]') for i in d.get('issues',[])]"
