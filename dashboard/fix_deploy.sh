#!/bin/bash
# Fix deploy.sh to use git fetch + reset instead of pull --ff-only (avoids merge conflicts)
sed -i 's/git pull --ff-only/git fetch origin \&\& git reset --hard origin\/main/g' /opt/itgyani-dashboard/deploy.sh
echo "Fixed deploy.sh:"
grep -E 'fetch|reset|pull' /opt/itgyani-dashboard/deploy.sh
