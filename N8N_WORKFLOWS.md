# n8n Workflow Inventory
*Extracted: 2026-04-25 | Source: n8n.itgyani.com*

## Summary
| Stat | Value |
|------|-------|
| Total Workflows | 8 |
| Active (Prod) | 3 |
| Dev/Inactive | 5 |
| Archived | 1 |

---

## 🟢 ACTIVE (Production) Workflows

### 1. Tamil to Hindi Voice-Over Shorts
- **ID:** PFkgegP6vDnFOUTN
- **Tag:** Dev (recently activated 2026-04-21)
- **Schedule:** Weekly, Monday 10:00 AM
- **Pipeline:**
  - Source: @nithyanandashorts (Tamil YouTube)
  - Download audio → Whisper STT (Tamil) → GPT-4.1 Translate → gpt-4o-mini-TTS (Hindi voice)
  - ffmpeg replace audio → MinIO storage → ffmpeg merge → Upload to @SPHNithyananda YouTube
  - Telegram notify → Ashish (chat 427179140)
- **Credentials needed:** YouTube OAuth2 for @SPHNithyananda (currently using @AI ASMR cred — WRONG)
- **Status:** ⚠️ Active but YouTube credential needs updating

### 2. UGC Ad - Status Check
- **ID:** 7RYILBPkdbKzH2pN
- **Tag:** Prod
- **Type:** Webhook GET `/ugc-ad-status?jobId=X`
- **Function:** Polls n8n execution status, returns video URL when done
- **Status:** ✅ Production ready

### 3. Social Media Poster via Zernio
- **ID:** yqqI4yT8jGwkOvVK
- **Tag:** Prod
- **Trigger:** Form submission
- **Function:** Post images (carousel) or video to Instagram + Twitter/X + Telegram via Zernio API
- **Platforms:** Instagram (69d61e987dea335c2bc5dd11), Twitter (69d6192a7dea335c2bc5ca11), Telegram (69d618e57dea335c2bc5c8a5)
- **Status:** ✅ Production ready

---

## 🔴 INACTIVE / Dev Workflows

### 4. Smart Job Hunter v1 - Multi-Portal Remote
- **ID:** BCUrXQnEBws13iTq
- **Tag:** Prod (but inactive)
- **Schedule:** Daily 9:00 AM IST (3:30 UTC)
- **Portals:** RemoteOK, Remotive, Himalayas, Jobicy, WeWorkRemotely, LinkedIn
- **AI Stack:** Azure GPT-4.1
- **Output:** Google Sheets + Gmail + Webhook
- **Status:** 🔴 Inactive — superseded by v2

### 5. Smart Job Hunter v2 - Multi-Portal (India + Middle East + Remote)
- **ID:** U3AMUubgOIqf5V31
- **Tag:** Dev
- **Schedule:** Daily 8:00 AM IST (2:30 UTC)
- **Portals:** LinkedIn India, LinkedIn Middle East, LinkedIn Remote, Remotive, Adzuna India*, Adzuna Gulf*, Jooble*, Arbeitnow, Himalayas, Naukri, RemoteOK (*needs API key)
- **AI Stack:** Anthropic Claude Sonnet 4.6 (resume parse) + Azure GPT-4.1 (scoring)
- **Target:** AI Director, GenAI Lead, Head of AI, VP AI roles
- **Output:** Google Sheets + Telegram alert to 427179140
- **Status:** 🔴 Inactive — needs Adzuna/Jooble keys + activation

### 6. Decodo Amazon Product Recommender
- **ID:** xSn0vDvDVHSSUtm3
- **Tag:** Dev
- **Trigger:** Telegram message
- **Function:** User sends product query → Decodo scrapes Amazon → AI recommends top picks
- **AI Stack:** Azure GPT-4.1
- **Status:** 🔴 Inactive (needs Decodo API key configured)

### 7. UGC Ad Creator - Form + AI Agent + Sora-2 + GDrive
- **ID:** DmobiLyNHjfPPu04
- **Tag:** Dev
- **Trigger:** Form submission
- **Function:** Upload product image → GPT-4.1 generates UGC script → Azure TTS voiceover → Sora-2 video generation → ffmpeg stitch → Google Drive → shareable link
- **AI Stack:** Azure GPT-4.1 + Sora-2 + Azure TTS
- **Status:** 🔴 Inactive (Sora-2 credits/access needed)

### 8. Vedic Astrology Agent (My workflow 2) — ARCHIVED
- **ID:** jJmj3WXXGuCl67ku
- **Status:** 🗑️ Archived

---

## 🔧 Infrastructure Dependencies

| Service | Purpose | Notes |
|---------|---------|-------|
| ffmpeg-api | Video processing | http://ffmpeg-api:8090 (internal Docker) |
| MinIO | Video temp storage | Bucket: dubbed-clips |
| Azure OpenAI (ditgenai-resource) | Whisper STT + TTS | Separate from ai-sambhatt3210 |
| Azure GPT-4.1 (AZURE Foundry) | AI scoring, scripts | Credential: mwEBezYniEFsl2Tr |
| Cloudinary | Image/video hosting | Account: ddh6nwmfq |
| Google Drive | Resume + video storage | OAuth2: OWGruANneRFzQE2k |
| Google Sheets | Job tracker | OAuth2: hJBjox7NAUhlDiXu |
| Zernio | Social media posting | API: zernio.com/api/v1/posts |
| Telegram (itgyani_bot) | Notifications | Cred: UCCaE2ISvudfveJs |
| Sora-2 | AI video generation | Azure: ditgenai-resource.cognitiveservices.azure.com |

---

## 📋 Priority Actions

### Immediate (this week)
1. **Fix Tamil Shorts YouTube cred** — swap @AI ASMR → @SPHNithyananda OAuth2
2. **Activate Job Hunter v2** — add Adzuna + Jooble keys, activate
3. **Update Job Hunter bot token** — point to @Job_Alert_Rony_Bot

### Next
4. **Activate Decodo Recommender** — add Decodo API key
5. **Test UGC Ad Creator** — verify Sora-2 access on ditgenai-resource
6. **Build email cleanup workflow** — MAYA's core task (8K+ emails, 8 accounts)
7. **Build lead database workflow** — 1M leads target for email marketing

---

## 🎯 New Workflows to Build (per Ashish direction)

### HIGH PRIORITY
- **Email Cleanup + Categorization** (Maya) — unsubscribe, categorize, priority flag
- **Lead Database Builder** — scrape + enrich contacts by category (target: 1M)
- **Email Marketing Sender** — bulk send with tracking, unsubscribe handling
- **Jira Auto-Ticket** — agent completions → Jira tickets via n8n webhook

### MEDIUM
- **Revenue Dashboard Updater** (Disha) — sync Engine 1 counter
- **SEO Content Publisher** (Priya) — auto-blog to itgyani.com
- **Uptime Monitor** (Kabir) — ping all services, alert on down

### PASSIVE INCOME (Engine 2)
- **Utility App SEO Pages** — programmatic pages from keyword data
- **AdSense Revenue Tracker** — pull earnings to dashboard
