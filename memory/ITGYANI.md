# ITGYANI — Company Context

## Overview
- **Company:** ITGYANI — Intelligent Automation Solutions
- **Owner:** Ashish (@cryptogyani_official)
- **Website:** https://itgyani.com
- **Mission:** Build & sell AI automation; grow Ashish's portfolio aggressively

## Properties
| Property | URL | Stack | Status |
|---|---|---|---|
| Main site | https://itgyani.com | Unknown | Live (thin landing page) |
| n8n server | https://n8n.itgyani.com | Self-hosted n8n | Live |
| Shopify store | https://kharadi-online.myshopify.com | Shopify | Live — Smart Kitchen Gadgets, India market |
| WooCommerce | https://kharadionline.com | WordPress+WooCommerce | Exists (to evaluate) |

## Shopify Store — Kharadi Online
- **Niche:** Smart Kitchen Gadgets for Indian homes (KitchenKraft brand)
- **USP:** Free shipping ₹499+, 7-day returns, direct from manufacturers
- **Market:** India (Mumbai, Delhi, Pune etc.)
- **Decision pending:** Keep Shopify OR consolidate on WooCommerce?

## Agent Team Plan
See AGENT_ROSTER.md

## Phase Priorities (from Ashish)
1. **Email consolidation & monitoring** — START HERE
2. Digital marketing + leads
3. n8n automation sales
4. Shopify/store management
5. Finance/trading tracking
6. HR / team building

## Communication
- All agent reports → Telegram (@cryptogyani_official)
- Notify Ashish ONLY for: decisions needed, critical failures, high-impact opportunities

## Email Accounts
| Account | Purpose |
|---|---|
| ashish@itgyani.com | ITGYANI main |
| ashish@cryptogyani.com | CryptoGyani personal |
| ashish@theemployeefactory.com | Employee Factory |
| ashish@technoflairlab.com | TechnoFlair Lab |
| info@cryptogyani.com | CryptoGyani public/info |
| trading@cryptogyani.com | Trading alerts/comms |
| support@theemployeefactory.com | Employee Factory support |

**Priority filters:** Clients + Job Leads
**Dashboard:** Will act as unified mail client
**Email access method:** App Password + IMAP (Option B) + Option C forwarding also acceptable
**ashish@itgyani.com:** Google Workspace
**All other custom domain emails:** Self-hosted VPS (IMAP)

## Tools Available
- OpenClaw (this system) — main COO agent
- n8n (self-hosted, Docker) — run locally first, migrate to prod VPS later
- Telegram — notifications
- No CRM, email platform, or ad accounts yet (building from scratch)

## Updated: 2026-04-22

## Marketing Database Schema (2026-04-23)
- **marketing_contacts** table: email, name, source_account, source_domain, first_seen_ts, tags, unsubscribed
- **marketing_phones** table: phone, name, email (FK optional), source, country_code, whatsapp_opted_in, added_ts, tags
- Both tables feed into email + WhatsApp marketing campaigns
- Sources: email inbox senders, Shopify orders (kharadionline.com), website signups (itgyani.com), manual import
- Export format: CSV for Mailchimp/Brevo, JSON for n8n automations

## Email Dashboard — Updated Rules (2026-04-23)
- **Delete** = Move to IMAP Trash on server (NOT local delete). Always recoverable.
- **Restore** = Move from Trash back to INBOX via IMAP
- **Reply** = Real SMTP send. Draft shown first → Ashish approves → then sends
- **Backup** = All emails backed up in SQLite before any destructive action
- **Goal** = Clean inbox to only important/addressed-to-me emails
- **Marketing DB** = Extract all sender emails → deduplicated master list for kharadionline.com + itgyani.com campaigns

## SMTP Credentials needed for reply:
- ashish@itgyani.com: App password already stored
- VPS accounts: SMTP via 194.233.64.74:587

## YouTube Channels (2026-04-23)
| Channel | Handle | Subscribers | Content |
|---|---|---|---|
| AnikaMiniBlox | @AnikaMiniBlox | 14 | Kids/gaming |
| Healorithm | @Healorithm | 19 | Health |
| Family Fun Adventures | @JoyfulFamilyMoments | 99 | Family |
| SehatSutra - Hindi | @SehatSutraHindi | 1 | Health Hindi |
| The Employee Factory | @theemployeefactory | 167 | HR/Recruitment |
| CryptoGyani Official | @CryptoGyaniOfficial | 52 | Crypto |
| AI ASMR 1Min | (AI ASMR) | 11 | ASMR |
| SPH Nithyananda - Hindi | - | 0 | Spiritual |

## n8n YouTube Automation Workflows Needed
- ASMR video auto-production pipeline
- Motivational video pipeline
- Health video pipeline (Healorithm + SehatSutra)
- Blog-to-video / blog auto-publish pipeline
- All workflows: generate script → TTS → visuals → upload to YouTube
