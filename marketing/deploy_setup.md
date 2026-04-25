# itgyani.com Auto-Deploy Setup

## How it works
- VPS polls GitHub every 5 minutes via `/home/itgyani.com/auto-deploy.sh`
- On new commit: git pull → bun install → bun build → cp to public_html
- On success: Telegram notification to Ashish (@cryptogyani_official)
- On failure: Telegram alert with log path
- Log: `/var/log/itgyani-auto-deploy.log`

## Landing Page
- URL: https://itgyani.com/ai-employee/
- File: /home/itgyani.com/public_html/ai-employee/index.html
- Source: /home/itgyani.com/landing/ai-employee/index.html (persists across deploys)

## Deploy manually
```bash
ssh rony@194.233.64.74
sudo /home/itgyani.com/auto-deploy.sh
```

## CTA Links
- Book call: https://cal.com/itgyani/15min
- WhatsApp: https://wa.me/919545550083
