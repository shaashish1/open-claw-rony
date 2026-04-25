# AI Models — ITGYANI Dashboard Panel
*For display on dashboard.itgyani.com — AI Models section*

---

## ✅ MODELS WE HAVE (Azure ai-sambhatt3210)

| Model | Provider | TPM | Best For | Cost Tier |
|-------|----------|-----|----------|-----------|
| claude-sonnet-4-6 | Anthropic (Azure) | 130,000 | Agent intelligence, analysis, writing | $$$ |
| claude-opus-4-6 | Anthropic (Azure) | 130,000 | Complex reasoning, strategy, code review | $$$$ |
| gpt-4o | OpenAI (Azure) | 250,000 | General tasks, vision, multimodal | $$$ |
| gpt-4o-mini-tts | OpenAI (Azure) | 100,000 | Text-to-speech, voice content, YouTube | $ |
| gpt-4o-transcribe | OpenAI (Azure) | 100,000 | Speech-to-text, meeting notes, audio | $ |
| gpt-5.3-codex | OpenAI (Azure) | — | Code generation, automation scripts | $$$ |

**Endpoint:** ai-sambhatt3210ai899661109114 (Azure)
**Expires:** Feb 2027 (claude), Oct 2026 (gpt-4o), Jun 2026 (transcribe)

---

## ✅ MODELS IN n8n (Already configured)

| Model | Credential in n8n | Used By |
|-------|-------------------|---------|
| Azure GPT-4.1 | AZURE Foundry GPT-4.1 (mwEBezYniEFsl2Tr) | Job Hunter, UGC Ad Creator |
| Azure Whisper | Azure GPT-4o-mini-TTS (w4U9MlsObTgi35Kp) | Tamil Shorts (STT) |
| Azure gpt-4o-mini-tts | Azure GPT-4o-mini-TTS | Tamil Shorts (TTS) |
| Anthropic Claude Sonnet 4.6 | Anthropic Online (PZoQqokVWvw4AuRm) | Job Hunter v2 resume parse |
| Sora-2 | Sora-2 (wt9gqLVx4MMKheK5) | UGC Ad video generation |

---

## ❌ MODELS WE NEED (Gaps)

### Immediate Needs

| Model | Use Case | Where to Get | Priority |
|-------|----------|--------------|----------|
| **Gemini 2.5 Pro** | SEO content, long-context analysis (2M tokens) | Google AI Studio / Vertex AI | 🔴 HIGH |
| **Perplexity API** | Real-time web search for INTEL agent | api.perplexity.ai | 🔴 HIGH |
| **ElevenLabs** | Premium voice TTS (better than gpt-4o-mini-tts) | elevenlabs.io | 🟡 MEDIUM |
| **Stable Diffusion / FLUX** | Image generation for content, ads | Replicate / FAL.ai | 🟡 MEDIUM |
| **Mistral Large** | Cost-effective European alternative | mistral.ai | 🟡 MEDIUM |

### For Algo Trading App

| Model | Use Case | Where to Get | Priority |
|-------|----------|--------------|----------|
| **FinBERT** | Financial sentiment analysis | HuggingFace | 🔴 HIGH |
| **TimesFM / Chronos** | Time series forecasting | Google Research / Amazon | 🔴 HIGH |
| **GPT-4o with function calling** | Trade signal generation | Already have via Azure | ✅ |

### For Job Search & Apply App

| Model | Use Case | Where to Get | Priority |
|-------|----------|--------------|----------|
| **Claude Sonnet** | Resume tailoring, cover letters | Already have via Azure | ✅ |
| **Gemini Flash** | Fast job description parsing (cheap) | Google AI Studio | 🟡 MEDIUM |
| **LinkedIn scraping** | Job discovery | Already in n8n Job Hunter | ✅ |

### For Email Marketing (1M leads)

| Model | Use Case | Where to Get | Priority |
|-------|----------|--------------|----------|
| **GPT-4o-mini** | Personalized email copy at scale | Azure (have gpt-4o, need mini) | 🔴 HIGH |
| **SendGrid / Mailgun API** | Bulk email delivery | Not AI but critical | 🔴 HIGH |

---

## 🗺️ AI Stack by Agent

| Agent | Current Model | Recommended Upgrade |
|-------|--------------|-------------------|
| RONY (COO) | claude-sonnet-4-6 | — (already optimal) |
| MAYA (Email) | claude-sonnet-4-6 | + GPT-4o-mini for bulk |
| ARJUN (Jobs) | claude-sonnet-4-6 | + Gemini Flash (fast parsing) |
| VIKRAM (Strategy) | claude-opus-4-6 | + Perplexity (real-time data) |
| NIKKI (Builder) | gpt-5.3-codex | — |
| PRIYA (SEO) | gpt-4o | + Gemini 2.5 Pro (long context) |
| DISHA (Analytics) | claude-sonnet-4-6 | + FinBERT (financial) |
| VEER (R&D) | gpt-4o | + Perplexity (trend research) |
| INTEL (Research) | gpt-4o | + Perplexity (web search) |
| YouTube Shorts | gpt-4o-mini-tts + Whisper | + ElevenLabs (premium voice) |
| UGC Ads | Sora-2 + GPT-4.1 | — |
| Algo Trading | OpenAlgo (running) | + FinBERT + TimesFM |

---

## 💰 Monthly API Cost Estimate (current)

| Service | Est. Monthly | Notes |
|---------|-------------|-------|
| Azure ai-sambhatt3210 | ~$200-400 | 130K TPM claude, 250K gpt-4o |
| n8n (self-hosted) | $0 | VPS hosted |
| Google Drive/Sheets | $0 | Free tier |
| Cloudinary | ~$0-25 | Free tier likely |
| **Total** | **~$200-425/mo** | |

### To Add
| Service | Est. Monthly |
|---------|-------------|
| Gemini 2.5 Pro | ~$50-100 |
| Perplexity API | ~$20-50 |
| SendGrid (1M emails) | ~$90-150 |
| ElevenLabs | ~$22-99 |
| **Additional** | **~$182-399** |
