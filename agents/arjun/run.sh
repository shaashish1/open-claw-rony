#!/bin/bash
cd /root/.openclaw/workspace/agents/arjun
export TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-""}
export AZURE_API_KEY=${AZURE_API_KEY:-""}
export AZURE_AI_URL=${AZURE_AI_URL:-"https://ai-sambhatt3210ai899661109114.services.ai.azure.com/anthropic/v1/messages"}
python3 arjun.py
