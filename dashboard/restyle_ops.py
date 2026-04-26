#!/usr/bin/env python3
"""
NIKKI Restyle Script for ops.html
Applies ai-side-hustles design language to dashboard.itgyani.com/ops
Run on VPS: python3 /tmp/restyle_ops.py
"""

import re
import shutil
import os

FILE = '/opt/itgyani-dashboard/frontend/ops.html'
BACKUP = FILE + '.bak'

# Read file
with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"[INFO] File size: {len(content)} bytes")

# Make backup
shutil.copy2(FILE, BACKUP)
print(f"[INFO] Backup: {BACKUP}")

# ============================================================
# 1. Replace <style> block with updated CSS
# ============================================================

NEW_STYLE = '''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*{box-sizing:border-box}
body{background:#0b0f1a;color:#f1f5f9;font-family:'Inter',system-ui,sans-serif;min-height:100vh;margin:0}
.card{background:#111827;border:1px solid #1f2937;border-radius:16px;transition:transform 0.2s,box-shadow 0.2s}
.card:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(99,102,241,0.15)}
.card2{background:#1a2235;border:1px solid #1f2937;border-radius:12px}
.nav-tab{padding:8px 16px;border-radius:8px;cursor:pointer;font-size:.8rem;font-weight:600;color:#6b7280;white-space:nowrap;transition:all 0.15s;border:1px solid transparent}
.nav-tab.active{background:linear-gradient(135deg,#1e1b4b,#1e293b);color:#a5b4fc;border:1px solid #3730a3}
.nav-tab:hover:not(.active){background:#1a2235;color:#94a3b8}
.sec{font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:#4b5563;font-weight:700;margin-bottom:8px}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block;flex-shrink:0}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.pulse{animation:pulse 2s infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.spin{width:12px;height:12px;border:2px solid #1f2937;border-top-color:#6366f1;border-radius:50%;animation:spin .8s linear infinite;display:inline-block;vertical-align:middle}
.pb{height:4px;background:#1f2937;border-radius:2px;overflow:hidden;margin-top:6px}
.pf{height:100%;border-radius:2px;transition:width .6s}
.pf-g{background:linear-gradient(90deg,#16a34a,#4ade80)}
.pf-b{background:linear-gradient(90deg,#4f46e5,#818cf8)}
.pf-o{background:linear-gradient(90deg,#ea580c,#fb923c)}
a{color:#818cf8}
input,textarea,select{background:#0b0f1a;border:1px solid #1f2937;border-radius:6px;color:#f1f5f9;padding:7px 11px;font-size:.85rem;outline:none}
.btn{padding:6px 14px;border-radius:8px;font-size:.8rem;font-weight:600;cursor:pointer;border:none;transition:opacity 0.15s}
.btn-p{background:linear-gradient(135deg,#4f46e5,#6366f1);color:#fff}
.btn-p:hover{opacity:0.9}
.btn-g{background:#1a2235;color:#94a3b8;border:1px solid #1f2937}
.btn-r{background:#7f1d1d;color:#fca5a5;border:none}
.sy{overflow-y:auto;scrollbar-width:thin}
.tp{display:block}.tp.hidden{display:none}
.acc-item{padding:8px 12px;cursor:pointer;border-radius:6px;font-size:.82rem}
.acc-item:hover{background:#1a2235}.acc-item.active{background:#1e2d40;color:#818cf8}
.erow{padding:10px 12px;cursor:pointer;border-bottom:1px solid #1f2937;font-size:.82rem}
.erow:hover{background:#1a2235}.erow.unread .esub{font-weight:700;color:#f1f5f9}
.tc{padding:10px;border-radius:8px;background:#1a2235;border:1px solid #1f2937;margin-bottom:6px;cursor:pointer;border-left:3px solid #6366f1;transition:transform 0.15s,box-shadow 0.15s}
.tc:hover{border-color:#374151;transform:translateY(-1px);box-shadow:0 4px 12px rgba(99,102,241,0.1)}.dnc{opacity:.4}
.kcol{background:linear-gradient(135deg,#111827,#1a2235);border:1px solid #1f2937;border-radius:16px;padding:10px;min-height:140px}
/* Agent card accent */
.agent-card{background:#1a2235;border:1px solid #1f2937;border-radius:14px;padding:12px;display:flex;flex-direction:column;gap:8px;border-left:3px solid #6366f1;transition:transform 0.2s,box-shadow 0.2s}
.agent-card:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(99,102,241,0.12)}
/* MOM entries */
.mom-card{background:#111827;border:1px solid #1f2937;border-radius:12px;padding:14px;margin-bottom:12px;border-left:4px solid #6366f1}
.mom-title{color:#f1f5f9;font-weight:700;font-size:0.95rem;margin-bottom:4px}
.mom-date{color:#94a3b8;font-size:0.75rem;margin-bottom:8px}
.mom-actions{list-style:none;padding:0;margin:0}
.mom-actions li{padding:4px 0;font-size:0.82rem;color:#94a3b8;display:flex;align-items:center;gap:6px}
.mom-actions li::before{content:"☐";color:#6366f1;font-size:0.9rem}
/* KPI stat cards */
.kpi-card{background:linear-gradient(135deg,#111827,#1a2235);border:1px solid #1f2937;border-radius:16px}
/* Glow dot for active agents */
.dot-active{box-shadow:0 0 6px #4ade80}
/* Scrollbar */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:#0b0f1a}
::-webkit-scrollbar-thumb{background:#1f2937;border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:#374151}
</style>'''

# Find and replace the style block
style_pattern = re.compile(r'<style>.*?</style>', re.DOTALL)
match = style_pattern.search(content)
if match:
    content = content[:match.start()] + NEW_STYLE + content[match.end():]
    print("[OK] Replaced <style> block")
else:
    print("[WARN] Could not find <style> block!")

# ============================================================
# 2. Add Inter font import to <head> (after charset meta)
#    Already included in @import in style block above
# ============================================================

# ============================================================
# 3. Replace the hero header (top bar)
# ============================================================

OLD_HERO = '''<div class="flex items-center justify-between mb-3 flex-wrap gap-2">
  <div class="flex items-center gap-2">
    <div class="dot pulse" style="background:#4ade80"></div>
    <span class="text-white font-bold text-sm">ITGYANI OS v3</span>
    <span class="text-xs px-2 py-0.5 rounded-full" style="background:#1e1b4b;color:#a5b4fc;border:1px solid #3730a3">Command Center</span>
  </div>
  <div class="flex items-center gap-2">
    <div id="clock" class="text-white font-mono font-bold text-sm hidden sm:block"></div>
    <div id="sync-lbl" class="text-slate-500 text-xs hidden sm:block">Syncing...</div>
    <button class="btn btn-g text-xs" onclick="loadAll()">Refresh</button>
    <a href="https://itgyani.atlassian.net/jira/software/projects/IT/boards/7" target="_blank" class="btn btn-p text-xs">Jira</a>
  </div>
</div>'''

NEW_HERO = '''<div style="background:linear-gradient(135deg,#1e1b4b 0%,#0b0f1a 60%);border-bottom:1px solid #312e81;padding:16px 20px;margin:-12px -12px 16px -12px;">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
    <div style="display:flex;align-items:center;gap:10px;">
      <div class="dot pulse dot-active" style="background:#4ade80;width:10px;height:10px;border-radius:50%;box-shadow:0 0 6px #4ade80"></div>
      <span style="font-size:1.4rem;font-weight:800;background:linear-gradient(135deg,#a5b4fc,#818cf8,#6366f1);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">ITGYANI OS v3</span>
      <span style="font-size:0.7rem;padding:3px 10px;border-radius:20px;background:#1e1b4b;color:#a5b4fc;border:1px solid #3730a3;font-weight:600;letter-spacing:0.05em;">COMMAND CENTER</span>
    </div>
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <div id="clock" style="font-family:monospace;font-size:0.85rem;color:#94a3b8;font-weight:600;"></div>
      <div id="sync-lbl" style="color:#6b7280;font-size:0.75rem;">Syncing...</div>
      <button class="btn btn-g text-xs" onclick="loadAll()">Refresh</button>
      <a href="https://itgyani.atlassian.net/jira/software/projects/IT/boards/7" target="_blank" class="btn btn-p text-xs">Jira</a>
    </div>
  </div>
</div>'''

if OLD_HERO in content:
    content = content.replace(OLD_HERO, NEW_HERO)
    print("[OK] Replaced hero header")
else:
    print("[WARN] Hero header not found by exact match — trying partial match...")
    # Try finding just the outer div by key markers
    hero_pattern = re.compile(
        r'<div class="flex items-center justify-between mb-3 flex-wrap gap-2">.*?</div>\s*</div>',
        re.DOTALL
    )
    hero_match = hero_pattern.search(content)
    if hero_match:
        content = content[:hero_match.start()] + NEW_HERO + content[hero_match.end():]
        print("[OK] Replaced hero header (partial match)")
    else:
        print("[WARN] Could not replace hero header")

# ============================================================
# 4. Upgrade KPI stat cards: add kpi-card class
# ============================================================
# The KPI cards use class="card p-3" — we add gradient via kpi-card on the top row
# They already inherit .card styles; the .kpi-card overrides background
# We'll add kpi-card class to the 6 top KPI cards
kpi_old = '<div class="card p-3"><div class="sec">Revenue MTD</div>'
kpi_new = '<div class="card kpi-card p-3"><div class="sec">Revenue MTD</div>'
if kpi_old in content:
    content = content.replace(kpi_old, kpi_new)
    print("[OK] Upgraded first KPI card (Revenue MTD)")

for sec_label in ['Strategies', 'ChartInk', 'Sprint 1', 'Agents Live', 'Projects']:
    old = f'<div class="card p-3"><div class="sec">{sec_label}</div>'
    new = f'<div class="card kpi-card p-3"><div class="sec">{sec_label}</div>'
    if old in content:
        content = content.replace(old, new)
        print(f"[OK] Upgraded KPI card: {sec_label}")

# ============================================================
# 5. Upgrade agent cards: add border-left and border-radius
# ============================================================
# Agent cards use inline style with border-radius:8px — upgrade to 14px + left accent
content = content.replace(
    'background:#1a2235;border:1px solid #1f2d40;border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:8px',
    'background:#1a2235;border:1px solid #1f2937;border-radius:14px;padding:12px;display:flex;flex-direction:column;gap:8px;border-left:3px solid #6366f1;transition:transform 0.2s,box-shadow 0.2s'
)
print("[OK] Upgraded agent card styles (radius + left accent)")

# ============================================================
# 6. Upgrade project cards: border-radius 10px -> 16px
# ============================================================
content = content.replace(
    'background:#111827;border:1px solid #1f2d40;border-radius:10px;padding:14px;display:flex',
    'background:#111827;border:1px solid #1f2937;border-radius:16px;padding:14px;display:flex'
)
print("[OK] Upgraded project card styles")

# ============================================================
# 7. Fix border color consistency: #1f2d40 -> #1f2937 in remaining inline styles
# ============================================================
content = content.replace('#1f2d40', '#1f2937')
print("[OK] Normalized border color to #1f2937")

# ============================================================
# 8. Active dot glow for agent status dots
# ============================================================
# Add glow to green (active) status dots in agent cards
content = content.replace(
    'background:#4ade80;animation:pulse 2s infinite;flex-shrink:0"></span>',
    'background:#4ade80;animation:pulse 2s infinite;flex-shrink:0;box-shadow:0 0 6px #4ade80"></span>'
)
print("[OK] Added glow to active agent status dots")

# ============================================================
# Write updated file
# ============================================================
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n[DONE] Written {len(content)} bytes to {FILE}")
print("[NEXT] Run: sudo systemctl restart itgyani-dashboard")
