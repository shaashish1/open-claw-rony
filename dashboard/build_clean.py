#!/usr/bin/env python3
"""Build clean ops.html - single file, no duplicates, all errors fixed"""
import os, json, base64, urllib.request

OUT = '/opt/itgyani-dashboard/frontend/ops.html'
J = 'https://itgyani.atlassian.net'

def jira_stats():
    try:
        tok = 'ATATT3xFfGF0GJ97pfigXVh7SDeOMP2c4ne74qmxi0n1t3Y6L93c9iNCim18ghom76w2g81qdDUvszrmqikeW5mlx_gJyd4zKklPfT_qgp6JRsz-FhCNsLP-knxeKBkTrSoSRGONbgPexGeWtwowxaADczDBtOQqx1xlInRqNQxcKg4ApeqYsQE=0C283DB8'
        em = 'ashish@itgyani.com'
        creds = base64.b64encode(f'{em}:{tok}'.encode()).decode()
        req = urllib.request.Request(
            f'{J}/rest/agile/1.0/board/7/issue?maxResults=50',
            headers={'Authorization':f'Basic {creds}','Accept':'application/json'})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read())
        total = d.get('total', 41)
        done = sum(1 for i in d.get('issues',[]) if i['fields']['status']['statusCategory']['key']=='done')
        prog = sum(1 for i in d.get('issues',[]) if i['fields']['status']['statusCategory']['key']=='indeterminate')
        return total, done, prog
    except Exception as e:
        print('Jira err:', e)
        return 41, 0, 0

total, done, prog = jira_stats()
pct = round(done/total*100) if total else 0

AGENTS = [
  ['RONY','COO','live','Sprint oversight + agent coordination + blocker escalation',72,'Sonnet',
   [['10/14','Agents Active'],['0/41','Sprint Done'],['0','Blockers']],
   [['IT-34','Agent KPI tiles'],['IT-35','QA dashboard panels']]],
  ['MAYA','CMO / Lead Gen','live','Email cleanup 8031 emails + 1M lead database build',45,'Haiku',
   [['0/8031','Emails Scanned'],['0/50K','Leads Built'],['0','Campaigns']],
   [['IT-26','Audit 8031 emails'],['IT-27','Email cleanup n8n'],['IT-28','Lead scraper 50K'],['IT-30','SendGrid']]],
  ['ARJUN','InfoSec','build','Security audit + job alert bot VPS deploy + RULE 0',30,'Sonnet',
   [['Clean','Secrets'],['0','Alerts Fired'],['0','Violations']],
   [['YUKTI-7','Security audit OpenAlgo'],['IT-38','Job scraper multi-portal']]],
  ['PRIYA','SEO Lead','live','CryptoGyani SEO launch - 10 articles/week + keywords',55,'Haiku',
   [['0/10','Articles'],['0/100','Keywords'],['Pending','AdSense']],
   [['CG-52','CryptoGyani SEO Launch'],['CG-55','GA4 + Search Console'],['CG-56','10 SEO articles'],['CG-59','Apply AdSense']]],
  ['ZARA','Sales','live','100 cold email prospects - fintech + SaaS founders',20,'Haiku',
   [['0/100','Prospects'],['0','Emails Sent'],['0','Replies']],
   [['IT-15','First 5 agency clients'],['IT-21','Cold email 100'],['IT-23','LinkedIn 50 DMs/day']]],
  ['FELIX','Support','plan','50-FAQ SOP library + support bot setup',5,'Haiku',
   [['0/50','FAQs'],['Not live','Support Bot'],['0','Tickets']],
   [['IT-11','Customer support bot']]],
  ['DISHA','PM','live','Sprint 1 daily standup + blocker escalation 30 min SLA',40,'Haiku',
   [['0','Blockers'],['N/A','On-time'],['At Risk','Sprint Health']],
   [['IT-1','Sprint 1 kickoff'],['IT-12','Admin dashboard']]],
  ['KABIR','DevOps','live','VPS hardening + Fyers auto-login + n8n YouTube production',85,'Haiku',
   [['10/10','Strategies Up'],['99.9%','VPS Uptime'],['16%','Disk Used']],
   [['YUKTI-3','Audit OpenAlgo VPS'],['YUKTI-4','Document broker config']]],
  ['NIKKI','Designer / QA','build','ITGYANI service page + QA gate for all UI before ship',35,'Haiku',
   [['Active','QA Gate'],['0/3','Pages Done'],['0','Bugs Found']],
   [['IT-20','Service menu pricing page'],['IT-4','Design service categories']]],
  ['VIKRAM','Analytics','live','Revenue KPI + daily P&L + ad performance tracking',50,'Haiku',
   [['Rs 0','Revenue MTD'],['N/A','Ad ROAS'],['0/7','Reports Done']],
   [['IT-33','AI model costs panel'],['YUKTI-6','P&L integration']]],
  ['ROHAN','Finance','live','Revenue tracking + cost monitoring + burn rate report',20,'Haiku',
   [['Rs 0','Revenue'],['Calculating','Burn Rate'],['Unknown','Runway']],
   [['IT-10','Payment setup']]],
  ['TARA','Research','live','Demand validation: Job App + OpenMAIC course scorecard',30,'Haiku',
   [['0/3','Products Validated'],['N/A','Scorecard'],['0/5','Reports']],
   [['IT-37','Demand landing page'],['IT-5','Research pain points']]],
  ['KIRAN','HR & Team Ops','plan','14-agent RACI matrix + onboarding SOP + roster',5,'Haiku',
   [['Pending','RACI Matrix'],['14/14','Agents'],['0/5','SOPs']],
   [['IT-6','Onboarding form']]],
  ['RAVI','RevOps / Payments','live','Razorpay + Stripe across all 7 properties - 7 days',15,'Haiku',
   [['0/7','Properties Live'],['Pending','Razorpay'],['Pending','Stripe']],
   [['IT-10','Payment setup'],['IT-41','Rs999 payment integration']]],
]

PROJECTS = [
  ['IT','ITGYANI Agency','active','high','AI automation agency - first 5 clients, service page, cold outreach','https://itgyani.com',J+'/jira/software/projects/IT/boards/7',41,0,0,'RONY/ZARA','Rs 0 → Rs 1L/mo',[['IT-15','First 5 clients'],['IT-20','Service page live'],['IT-21','100 cold emails']]],
  ['CG','CryptoGyani.com','active','high','SEO crypto blog + AdSense + newsletter passive income','https://cryptogyani.com',J+'/jira/software/projects/CG/boards',54,4,0,'PRIYA','AdSense passive income',[['CG-52','SEO launch'],['CG-56','10 articles/week'],['CG-59','Apply AdSense']]],
  ['YUKTI','Yukti Algo Trading','active','high','OpenAlgo algo trading SaaS - 10 strategies in analyze mode','https://openalgo.cryptogyani.com',J+'/jira/software/projects/YUKTI/boards',7,0,0,'KABIR/VIKRAM','Rs 1Cr paper → SaaS beta',[['YUKTI-3','VPS audit'],['YUKTI-5','Trading dashboard'],['YUKTI-6','P&L integration']]],
  ['TEF','The Employee Factory','active','med','OpenMAIC LMS - HR and career courses','https://learn.theemployeefactory.com',J+'/jira/software/projects/TEF/boards',21,0,1,'TARA/FELIX','Rs 0 → course revenue',[['TEF-15','LMS go-live'],['TEF-16','First course'],['TEF-17','OpenMAIC live']]],
  ['KO','Kharadi Online','active','low','Self-hosted ecom - Amazon affiliate, local store','https://kharadionline.com',J+'/jira/software/projects/KO/boards',5,0,0,'RAVI','Amazon affiliate ROAS 2x',[['KO-13','ROAS 2x campaign'],['KO-12','Amazon affiliate'],['KO-11','Store sync']]],
  ['JOB','AI Job Alert App','build','med','Telegram bot - LinkedIn scraper, AI scoring, Telegram alerts','https://t.me/Job_Alert_Rony_Bot',J+'/jira/software/projects/IT/boards/7',6,0,1,'ARJUN','Rs 999/mo subscription',[['IT-37','Demand validation'],['IT-38','Job scraper'],['IT-42','Beta 10 users']]],
  ['QPF','QuickPay Finance','plan','low','India crypto exchange + FIAT gateway + DEX','#',J+'/jira/software/projects/QPF/boards',3,0,0,'TARA','Long-term SaaS',[['QPF-1','India exchange'],['QPF-2','On/Off ramp'],['QPF-3','DEX']]],
  ['SF','SendMoney Finance','plan','low','International money transfer + stablecoin INRT','#',J+'/jira/software/projects/SF/boards',7,0,0,'TARA','Long-term fintech',[['SF-1','Landing branding'],['SF-6','Stablecoin INRT'],['SF-2','KYC dashboard']]],
]

def uc(u):
    return '#4ade80' if u>=70 else '#fbbf24' if u>=40 else '#818cf8'

def ring(u):
    c=uc(u); r=22; ci=2*3.14159*r; off=ci-(u/100)*ci
    return (f'<svg style="transform:rotate(-90deg)" width="52" height="52" viewBox="0 0 52 52">'
            f'<circle fill="none" stroke="#1f2d40" stroke-width="5" cx="26" cy="26" r="{r}"/>'
            f'<circle fill="none" stroke-width="5" stroke-linecap="round" cx="26" cy="26" r="{r}" stroke="{c}" '
            f'stroke-dasharray="{ci:.1f}" stroke-dashoffset="{off:.1f}"/></svg>')

def sbadge(s):
    if s=='live': return '<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;background:#052e16;color:#4ade80;border:1px solid #166534">LIVE</span>'
    if s=='build': return '<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;background:#1c1917;color:#fb923c;border:1px solid #9a3412">BUILDING</span>'
    return '<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;background:#1e1b4b;color:#818cf8;border:1px solid #3730a3">PLANNED</span>'

def pbadge(p):
    if p=='high': return '<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;background:#450a0a;color:#f87171;border:1px solid #991b1b">HIGH</span>'
    if p=='med': return '<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;background:#1c1917;color:#fbbf24;border:1px solid #92400e">MED</span>'
    return '<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;background:#111827;color:#6b7280;border:1px solid #374151">LOW</span>'

agent_html = ''
for a in AGENTS:
    name,role,status,task,util,model,kpis,jira_links = a
    rc = uc(util)
    dot_anim = 'animation:pulse 2s infinite' if status in ('live','build') else ''
    dot_col = '#4ade80' if status=='live' else '#fb923c' if status=='build' else '#818cf8'
    kpi_h = ''.join(f'<div style="text-align:center"><div style="font-size:.65rem;color:#6b7280;margin-bottom:2px">{k[1]}</div><div style="color:#e2e8f0;font-size:.85rem;font-weight:700">{k[0]}</div></div>' for k in kpis)
    ji_h = ''.join(f'<a href="{J}/browse/{j[0]}" target="_blank" style="display:flex;align-items:center;gap:4px;text-decoration:none;margin-bottom:3px"><span style="color:#818cf8;font-family:monospace;font-size:.7rem;flex-shrink:0">{j[0]}</span><span style="color:#6b7280;font-size:.72rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:170px">{j[1]}</span></a>' for j in jira_links)
    agent_html += (
        f'<div style="background:#1a2235;border:1px solid #1f2d40;border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:8px">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
        f'<div style="display:flex;align-items:center;gap:8px">'
        f'<span style="width:7px;height:7px;border-radius:50%;display:inline-block;background:{dot_col};{dot_anim};flex-shrink:0"></span>'
        f'<div><div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">'
        f'<span style="color:#fff;font-weight:700;font-size:.85rem">{name}</span>{sbadge(status)}</div>'
        f'<div style="color:#6b7280;font-size:.72rem">{role}</div></div></div>'
        f'<div style="position:relative;width:52px;height:52px;flex-shrink:0">{ring(util)}'
        f'<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:700;color:{rc}">{util}%</div></div></div>'
        f'<div style="color:#6b7280;font-size:.75rem;line-height:1.5;border-left:2px solid #334155;padding-left:8px">{task}</div>'
        f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px;background:rgba(15,23,42,.4);border-radius:6px;padding:8px">{kpi_h}</div>'
        f'<div><div style="font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#374151;margin-bottom:4px">Jira Tickets</div>{ji_h}</div>'
        f'<div style="display:flex;justify-content:space-between;padding-top:6px;border-top:1px solid #1f2d40">'
        f'<span style="color:#4b5563;font-size:.7rem">Model: <span style="color:#6b7280">{model}</span></span>'
        f'<span style="font-size:.7rem;font-weight:700;color:{rc}">{util}% util</span></div></div>\n'
    )

proj_html = ''
for p in PROJECTS:
    key,name,status,prio,desc,url,jurl,ti,di,pi,owner,rev,miles = p
    pp = round(di/ti*100) if ti else 0
    m_h = ''.join(f'<a href="{J}/browse/{m[0]}" target="_blank" style="display:flex;align-items:center;gap:4px;text-decoration:none;margin-bottom:3px"><span style="color:#818cf8;font-family:monospace;font-size:.7rem;flex-shrink:0">{m[0]}</span><span style="color:#6b7280;font-size:.72rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{m[1]}</span></a>' for m in miles)
    live_b = f'<a href="{url}" target="_blank" style="flex:1;text-align:center;padding:5px 8px;border-radius:6px;font-size:.78rem;font-weight:600;background:#1a2235;color:#94a3b8;border:1px solid #1f2d40;text-decoration:none">Live</a>' if url != '#' else ''
    proj_html += (
        f'<div style="background:#111827;border:1px solid #1f2d40;border-radius:10px;padding:14px;display:flex;flex-direction:column;gap:8px">'
        f'<div><div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:3px">'
        f'<span style="color:#fff;font-weight:700">{name}</span>{sbadge(status)}{pbadge(prio)}</div>'
        f'<div style="color:#6b7280;font-size:.72rem">{desc}</div></div>'
        f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;text-align:center;background:rgba(15,23,42,.4);border-radius:6px;padding:8px">'
        f'<div><div style="color:#4ade80;font-weight:700;font-size:1.2rem">{di}</div><div style="color:#4b5563;font-size:.65rem">Done</div></div>'
        f'<div><div style="color:#fb923c;font-weight:700;font-size:1.2rem">{pi}</div><div style="color:#4b5563;font-size:.65rem">In Prog</div></div>'
        f'<div><div style="color:#e2e8f0;font-weight:700;font-size:1.2rem">{ti-di-pi}</div><div style="color:#4b5563;font-size:.65rem">To Do</div></div></div>'
        f'<div style="height:4px;background:#1f2d40;border-radius:2px;overflow:hidden"><div style="height:100%;width:{pp}%;background:linear-gradient(90deg,#16a34a,#4ade80)"></div></div>'
        f'<div style="display:flex;justify-content:space-between;font-size:.72rem;color:#6b7280"><span>{pp}% — {ti} issues</span><span>{owner}</span></div>'
        f'<div style="font-size:.72rem;color:#6b7280">{rev}</div>'
        f'<div style="padding-top:6px;border-top:1px solid #1f2d40"><div style="font-size:.6rem;font-weight:700;text-transform:uppercase;color:#374151;margin-bottom:4px">Next Milestones</div>{m_h}</div>'
        f'<div style="display:flex;gap:6px">{live_b}'
        f'<a href="{jurl}" target="_blank" style="flex:1;text-align:center;padding:5px 8px;border-radius:6px;font-size:.78rem;font-weight:600;background:#1a2235;color:#94a3b8;border:1px solid #1f2d40;text-decoration:none">Jira Board</a></div></div>\n'
    )

# ---- Write complete HTML ----
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ITGYANI OS v3 - Command Center</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
*{{box-sizing:border-box}}
body{{background:#0b0f1a;color:#e2e8f0;font-family:system-ui,sans-serif;min-height:100vh;margin:0}}
.card{{background:#111827;border:1px solid #1f2d40;border-radius:10px}}
.card2{{background:#1a2235;border:1px solid #1f2d40;border-radius:8px}}
.nav-tab{{padding:7px 14px;border-radius:6px;cursor:pointer;font-size:.8rem;font-weight:600;color:#6b7280;white-space:nowrap}}
.nav-tab.active{{background:#1e293b;color:#e2e8f0}}
.sec{{font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:#4b5563;font-weight:700;margin-bottom:8px}}
.dot{{width:7px;height:7px;border-radius:50%;display:inline-block;flex-shrink:0}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
.pulse{{animation:pulse 2s infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.spin{{width:12px;height:12px;border:2px solid #1f2d40;border-top-color:#6366f1;border-radius:50%;animation:spin .8s linear infinite;display:inline-block;vertical-align:middle}}
.pb{{height:4px;background:#1f2d40;border-radius:2px;overflow:hidden;margin-top:6px}}
.pf{{height:100%;border-radius:2px;transition:width .6s}}
.pf-g{{background:linear-gradient(90deg,#16a34a,#4ade80)}}
.pf-b{{background:linear-gradient(90deg,#4f46e5,#818cf8)}}
.pf-o{{background:linear-gradient(90deg,#ea580c,#fb923c)}}
a{{color:#818cf8}}
input,textarea,select{{background:#0b0f1a;border:1px solid #1f2d40;border-radius:6px;color:#e2e8f0;padding:7px 11px;font-size:.85rem;outline:none}}
.btn{{padding:6px 14px;border-radius:6px;font-size:.8rem;font-weight:600;cursor:pointer;border:none}}
.btn-p{{background:#4f46e5;color:#fff}}.btn-g{{background:#1a2235;color:#94a3b8;border:1px solid #1f2d40}}
.btn-r{{background:#7f1d1d;color:#fca5a5;border:none}}
.sy{{overflow-y:auto;scrollbar-width:thin}}
.tp{{display:block}}.tp.hidden{{display:none}}
.acc-item{{padding:8px 12px;cursor:pointer;border-radius:6px;font-size:.82rem}}
.acc-item:hover{{background:#1a2235}}.acc-item.active{{background:#1e2d40;color:#818cf8}}
.erow{{padding:10px 12px;cursor:pointer;border-bottom:1px solid #1f2d40;font-size:.82rem}}
.erow:hover{{background:#1a2235}}.erow.unread .esub{{font-weight:700;color:#e2e8f0}}
.tc{{padding:10px;border-radius:6px;background:#1a2235;border:1px solid #1f2d40;margin-bottom:6px;cursor:pointer}}
.tc:hover{{border-color:#374151}}.dnc{{opacity:.4}}
.kcol{{background:#111827;border:1px solid #1f2d40;border-radius:8px;padding:10px;min-height:140px}}
</style>
</head>
<body class="p-3">

<div class="flex items-center justify-between mb-3 flex-wrap gap-2">
  <div class="flex items-center gap-2">
    <div class="dot pulse" style="background:#4ade80"></div>
    <span class="text-white font-bold text-sm">ITGYANI OS v3</span>
    <span class="text-xs px-2 py-0.5 rounded-full" style="background:#1e1b4b;color:#a5b4fc;border:1px solid #3730a3">Command Center</span>
  </div>
  <div class="flex items-center gap-2">
    <div id="clock" class="text-white font-mono font-bold text-sm hidden sm:block"></div>
    <div id="sync-lbl" class="text-slate-500 text-xs hidden sm:block">Syncing...</div>
    <button class="btn btn-g text-xs" onclick="loadAll()">Refresh</button>
    <a href="{J}/jira/software/projects/IT/boards/7" target="_blank" class="btn btn-p text-xs">Jira</a>
  </div>
</div>

<div class="grid grid-cols-2 md:grid-cols-6 gap-2 mb-3">
  <div class="card p-3"><div class="sec">Revenue MTD</div><div class="text-xl font-bold text-white">Rs 0</div><div class="text-xs text-slate-500">Target Rs 1L/mo</div><div class="pb"><div class="pf pf-b" style="width:1%"></div></div></div>
  <div class="card p-3"><div class="sec">Strategies</div><div id="k-s" class="text-xl font-bold text-green-400"><span class="spin"></span></div><div class="text-xs text-slate-500">Analyze mode</div><div class="pb"><div class="pf pf-g" id="k-s-b" style="width:0%"></div></div></div>
  <div class="card p-3"><div class="sec">ChartInk</div><div id="k-c" class="text-xl font-bold text-green-400"><span class="spin"></span></div><div class="text-xs text-slate-500">to OpenAlgo</div><div class="pb"><div class="pf pf-g" style="width:100%"></div></div></div>
  <div class="card p-3"><div class="sec">Sprint 1</div><div id="k-j" class="text-xl font-bold text-white">{done}/{total}</div><div id="k-j-l" class="text-xs text-slate-500">{done} done / {total} issues</div><div class="pb"><div class="pf pf-b" style="width:{pct}%"></div></div></div>
  <div class="card p-3"><div class="sec">Agents Live</div><div class="text-xl font-bold" style="color:#818cf8">10<span class="text-slate-500 text-sm">/14</span></div><div class="text-xs text-slate-500">4 building/planned</div><div class="pb"><div class="pf pf-b" style="width:71%"></div></div></div>
  <div class="card p-3"><div class="sec">Projects</div><div class="text-xl font-bold text-yellow-400">8</div><div class="text-xs text-slate-500">5 Active / 3 Planned</div><div class="pb"><div class="pf pf-o" style="width:63%"></div></div></div>
</div>

<div class="flex gap-1 mb-3 p-1 rounded-lg overflow-x-auto" style="background:#0f172a">
  <div class="nav-tab active" onclick="switchTab('agents',this)">Agents + KPIs</div>
  <div class="nav-tab" onclick="switchTab('projects',this)">Projects</div>
  <div class="nav-tab" onclick="switchTab('mailbox',this)">Mailbox</div>
  <div class="nav-tab" onclick="switchTab('tasks',this)">Tasks</div>
  <div class="nav-tab" onclick="switchTab('sprint',this)">Sprint</div>
  <div class="nav-tab" onclick="switchTab('systems',this)">Systems</div>
  <div class="nav-tab" onclick="switchTab('logs',this)">Logs</div>
</div>

<div id="tp-agents" class="tp">
  <div style="font-size:.7rem;color:#4b5563;margin-bottom:12px;letter-spacing:.05em">PERFORMANCE &amp; UTILIZATION — ALL 14 AGENTS | Ring = estimated utilization</div>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
{agent_html}  </div>
</div>

<div id="tp-projects" class="tp hidden">
  <div style="font-size:.7rem;color:#4b5563;margin-bottom:12px;letter-spacing:.05em">8 PROPERTIES | IT · CG · YUKTI · TEF · KO · JOB · QPF · SF — linked to Jira boards</div>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
{proj_html}  </div>
</div>

<div id="tp-mailbox" class="tp hidden">
  <div class="card" style="height:calc(100vh - 230px);display:flex;overflow:hidden">
    <div style="width:190px;border-right:1px solid #1f2d40;display:flex;flex-direction:column">
