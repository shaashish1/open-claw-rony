#!/usr/bin/env python3
"""Inject agent_cards and proj_cards into ops.html on VPS"""
import os

OUT = '/opt/itgyani-dashboard/frontend/ops.html'

with open(OUT, 'r') as f:
    html = f.read()

# Check if already injected
if 'card2 p-3' in html or 'rw' in html[:5000]:
    print("Cards already injected or different format")

# Re-run the generation logic inline
import sys
sys.path.insert(0, '/tmp')

# Re-generate the cards directly
J = 'https://itgyani.atlassian.net'

AGENTS = [
  ['RONY','COO','live','Sprint oversight + agent coordination + blocker escalation',72,'Sonnet',
   [['10/14','Agents Active'],['0/41','Sprint Done'],['0','Blockers']],
   [['IT-34','Agent KPI tiles'],['IT-35','QA dashboard panels']]],
  ['MAYA','CMO','live','Email cleanup 8031 emails + 1M lead database build',45,'Haiku',
   [['0/8031','Emails Scanned'],['0/50K','Leads Built'],['0','Campaigns']],
   [['IT-26','Audit 8031 emails'],['IT-27','Email cleanup n8n'],['IT-28','Lead scraper 50K'],['IT-30','SendGrid']]],
  ['ARJUN','InfoSec','build','Security audit + job alert bot VPS deploy + RULE 0',30,'Sonnet',
   [['Clean','Secrets'],['0','Alerts Fired'],['0','Violations']],
   [['YUKTI-7','Security audit OpenAlgo'],['IT-38','Job scraper']]],
  ['PRIYA','SEO Lead','live','CryptoGyani SEO launch - 10 articles/week + keywords',55,'Haiku',
   [['0/10','Articles'],['0/100','Keywords'],['Pending','AdSense']],
   [['CG-52','CryptoGyani SEO Launch'],['CG-55','GA4 Setup'],['CG-56','10 SEO articles'],['CG-59','Apply AdSense']]],
  ['ZARA','Sales','live','100 cold email prospects - fintech + SaaS founders',20,'Haiku',
   [['0/100','Prospects'],['0','Emails Sent'],['0','Replies']],
   [['IT-15','First 5 clients'],['IT-21','Cold email 100'],['IT-23','LinkedIn 50 DMs/day']]],
  ['FELIX','Support','plan','50-FAQ SOP library + support bot setup',5,'Haiku',
   [['0/50','FAQs'],['Not live','Support Bot'],['0','Tickets']],
   [['IT-11','Customer support bot']]],
  ['DISHA','PM','live','Sprint 1 daily standup + blocker escalation 30 min SLA',40,'Haiku',
   [['0','Blockers'],['N/A','On-time'],['At Risk','Sprint Health']],
   [['IT-1','Sprint 1 kickoff'],['IT-12','Admin dashboard']]],
  ['KABIR','DevOps','live','VPS hardening + Fyers auto-login + n8n YouTube production',85,'Haiku',
   [['10/10','Strategies Up'],['99.9%','VPS Uptime'],['16%','Disk Used']],
   [['YUKTI-3','Audit OpenAlgo VPS'],['YUKTI-4','Broker config doc']]],
  ['NIKKI','Designer / QA','build','ITGYANI service page + QA gate for all UI',35,'Haiku',
   [['Active','QA Gate'],['0/3','Pages Done'],['0','Bugs Found']],
   [['IT-20','Service menu pricing'],['IT-4','Design categories']]],
  ['VIKRAM','Analytics','live','Revenue KPI + daily P&L + ad performance',50,'Haiku',
   [['Rs 0','Revenue MTD'],['N/A','Ad ROAS'],['0/7','Reports Done']],
   [['IT-33','AI model costs'],['YUKTI-6','P&L integration']]],
  ['ROHAN','Finance','live','Revenue tracking + cost monitoring + burn rate',20,'Haiku',
   [['Rs 0','Revenue'],['Calculating','Burn Rate'],['Unknown','Runway']],
   [['IT-10','Payment setup']]],
  ['TARA','Research','live','Demand validation: Job App + OpenMAIC course scorecard',30,'Haiku',
   [['0/3','Products Validated'],['N/A','Scorecard'],['0/5','Reports']],
   [['IT-37','Demand landing'],['IT-5','Research pain points']]],
  ['KIRAN','HR & Team Ops','plan','14-agent RACI + onboarding SOP + roster',5,'Haiku',
   [['Pending','RACI Matrix'],['14/14','Agents'],['0/5','SOPs']],
   [['IT-6','Onboarding form']]],
  ['RAVI','RevOps / Payments','live','Razorpay + Stripe across all 7 properties - 7 days',15,'Haiku',
   [['0/7','Properties Live'],['Pending','Razorpay'],['Pending','Stripe']],
   [['IT-10','Payment setup'],['IT-41','Rs999 payment']]],
]

PROJECTS = [
  ['IT','ITGYANI Agency','active','high','AI automation agency - first 5 clients service page outreach','https://itgyani.com',J+'/jira/software/projects/IT/boards/7',41,0,0,'RONY/ZARA','Rs 0 to Rs 1L/mo',[['IT-15','First 5 clients'],['IT-20','Service page'],['IT-21','100 cold emails']]],
  ['CG','CryptoGyani.com','active','high','SEO crypto blog + AdSense + newsletter passive income','https://cryptogyani.com',J+'/jira/software/projects/CG/boards',54,4,0,'PRIYA','AdSense passive income',[['CG-52','SEO launch'],['CG-56','10 articles'],['CG-59','AdSense apply']]],
  ['YUKTI','Yukti Algo Trading','active','high','OpenAlgo algo trading SaaS 10 strategies analyze mode','https://openalgo.cryptogyani.com',J+'/jira/software/projects/YUKTI/boards',7,0,0,'KABIR/VIKRAM','Rs 1Cr paper to SaaS',[['YUKTI-3','VPS audit'],['YUKTI-5','Trading dashboard'],['YUKTI-6','P&L integration']]],
  ['TEF','The Employee Factory','active','med','OpenMAIC LMS HR and career courses','https://learn.theemployeefactory.com',J+'/jira/software/projects/TEF/boards',21,0,1,'TARA/FELIX','Rs 0 to course revenue',[['TEF-15','LMS go-live'],['TEF-16','First course'],['TEF-17','OpenMAIC live']]],
  ['KO','Kharadi Online','active','low','Self-hosted ecom Amazon affiliate local store','https://kharadionline.com',J+'/jira/software/projects/KO/boards',5,0,0,'RAVI','Amazon affiliate ROAS 2x',[['KO-13','ROAS 2x'],['KO-12','Amazon affiliate'],['KO-11','Store sync']]],
  ['JOB','AI Job Alert App','build','med','Telegram bot LinkedIn scraper AI scoring alerts','https://t.me/Job_Alert_Rony_Bot',J+'/jira/software/projects/IT/boards/7',6,0,1,'ARJUN','Rs 999/mo subscription',[['IT-37','Demand validation'],['IT-38','Job scraper'],['IT-42','Beta 10 users']]],
  ['QPF','QuickPay Finance','plan','low','India crypto exchange FIAT gateway DEX','#',J+'/jira/software/projects/QPF/boards',3,0,0,'TARA','Long-term SaaS',[['QPF-1','India exchange'],['QPF-2','On/Off ramp'],['QPF-3','DEX']]],
  ['SF','SendMoney Finance','plan','low','International money transfer stablecoin INRT','#',J+'/jira/software/projects/SF/boards',7,0,0,'TARA','Long-term fintech',[['SF-1','Landing branding'],['SF-6','Stablecoin INRT'],['SF-2','KYC dashboard']]],
]

def uc(u):
    return '#4ade80' if u>=70 else '#fbbf24' if u>=40 else '#818cf8'

def ring(u):
    c=uc(u); r=22; ci=2*3.14159*r; off=ci-(u/100)*ci
    return (f'<svg style="transform:rotate(-90deg)" width=52 height=52 viewBox="0 0 52 52">'
            f'<circle fill=none stroke=#1f2d40 stroke-width=5 cx=26 cy=26 r={r}/>'
            f'<circle fill=none stroke-width=5 stroke-linecap=round cx=26 cy=26 r={r} stroke={c} '
            f'stroke-dasharray={ci:.1f} stroke-dashoffset={off:.1f}/></svg>')

def st_badge(s):
    if s=='live': return '<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;background:#052e16;color:#4ade80;border:1px solid #166534">LIVE</span>'
    if s=='build': return '<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;background:#1c1917;color:#fb923c;border:1px solid #9a3412">BUILDING</span>'
    return '<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;background:#1e1b4b;color:#818cf8;border:1px solid #3730a3">PLANNED</span>'

def pr_badge(p):
    if p=='high': return '<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;background:#450a0a;color:#f87171;border:1px solid #991b1b">HIGH</span>'
    if p=='med': return '<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;background:#1c1917;color:#fbbf24;border:1px solid #92400e">MED</span>'
    return '<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;background:#111827;color:#6b7280;border:1px solid #374151">LOW</span>'

agent_html = ''
for a in AGENTS:
    name,role,status,task,util,model,kpis,jira_links = a
    rc = uc(util)
    dt_style = f'background:{rc};animation:P 2s infinite' if status in ('live','build') else 'background:#818cf8'
    kpi_h = ''.join(f'<div style=text-align:center><div style="font-size:.65rem;color:#6b7280;margin-bottom:2px">{k[1]}</div><div style="color:#e2e8f0;font-size:.85rem;font-weight:700">{k[0]}</div></div>' for k in kpis)
    ji_h = ''.join(f'<a href={J}/browse/{j[0]} target=_blank style="display:flex;align-items:center;gap:4px;text-decoration:none;margin-bottom:3px"><span style="color:#818cf8;font-family:monospace;font-size:.7rem;flex-shrink:0">{j[0]}</span><span style="color:#6b7280;font-size:.72rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:160px">{j[1]}</span></a>' for j in jira_links)
    agent_html += (
        f'<div style="background:#1a2235;border:1px solid #1f2d40;border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:8px">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
        f'<div style="display:flex;align-items:center;gap:8px">'
        f'<span style="width:7px;height:7px;border-radius:50%;display:inline-block;{dt_style}"></span>'
        f'<div><div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">'
        f'<span style="color:#fff;font-weight:700;font-size:.85rem">{name}</span>{st_badge(status)}</div>'
        f'<div style="color:#6b7280;font-size:.72rem">{role}</div></div></div>'
        f'<div style="position:relative;width:52px;height:52px;flex-shrink:0">{ring(util)}'
        f'<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:700;color:{rc}">{util}%</div></div></div>'
        f'<div style="color:#6b7280;font-size:.75rem;line-height:1.5;border-left:2px solid #334155;padding-left:8px">{task}</div>'
        f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px;background:#0f172a60;border-radius:6px;padding:8px">{kpi_h}</div>'
        f'<div><div style="font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#374151;margin-bottom:4px">Jira Tickets</div>{ji_h}</div>'
        f'<div style="display:flex;justify-content:space-between;padding-top:6px;border-top:1px solid #1f2d40">'
        f'<span style="color:#4b5563;font-size:.7rem">Model: <span style=color:#6b7280>{model}</span></span>'
        f'<span style="font-size:.7rem;font-weight:700;color:{rc}">{util}% util</span></div></div>\n'
    )

proj_html = ''
for p in PROJECTS:
    key,name,status,prio,desc,url,jurl,ti,di,pi,owner,rev,miles = p
    pp = round(di/ti*100) if ti else 0
    m_h = ''.join(f'<a href={J}/browse/{m[0]} target=_blank style="display:flex;align-items:center;gap:4px;text-decoration:none;margin-bottom:3px"><span style="color:#818cf8;font-family:monospace;font-size:.7rem;flex-shrink:0">{m[0]}</span><span style="color:#6b7280;font-size:.72rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{m[1]}</span></a>' for m in miles)
    live_b = f'<a href={url} target=_blank style="flex:1;text-align:center;padding:5px 8px;border-radius:6px;font-size:.78rem;font-weight:600;background:#1a2235;color:#94a3b8;border:1px solid #1f2d40;text-decoration:none">Live</a>' if url != '#' else ''
    proj_html += (
        f'<div style="background:#111827;border:1px solid #1f2d40;border-radius:10px;padding:14px;display:flex;flex-direction:column;gap:8px">'
        f'<div><div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:3px">'
        f'<span style="color:#fff;font-weight:700">{name}</span>{st_badge(status)}{pr_badge(prio)}</div>'
        f'<div style="color:#6b7280;font-size:.72rem">{desc}</div></div>'
        f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;text-align:center;background:#0f172a60;border-radius:6px;padding:8px">'
        f'<div><div style="color:#4ade80;font-weight:700;font-size:1.2rem">{di}</div><div style="color:#4b5563;font-size:.65rem">Done</div></div>'
        f'<div><div style="color:#fb923c;font-weight:700;font-size:1.2rem">{pi}</div><div style="color:#4b5563;font-size:.65rem">In Prog</div></div>'
        f'<div><div style="color:#e2e8f0;font-weight:700;font-size:1.2rem">{ti-di-pi}</div><div style="color:#4b5563;font-size:.65rem">To Do</div></div></div>'
        f'<div style="height:4px;background:#1f2d40;border-radius:2px;overflow:hidden"><div style="height:100%;width:{pp}%;background:linear-gradient(90deg,#16a34a,#4ade80)"></div></div>'
        f'<div style="display:flex;justify-content:space-between;font-size:.72rem;color:#6b7280"><span>{pp}% - {ti} issues</span><span>{owner}</span></div>'
        f'<div style="font-size:.72rem;color:#6b7280">{rev}</div>'
        f'<div style="padding-top:6px;border-top:1px solid #1f2d40"><div style="font-size:.6rem;font-weight:700;text-transform:uppercase;color:#374151;margin-bottom:4px">Next Milestones</div>{m_h}</div>'
        f'<div style="display:flex;gap:6px">{live_b}'
        f'<a href={jurl} target=_blank style="flex:1;text-align:center;padding:5px 8px;border-radius:6px;font-size:.78rem;font-weight:600;background:#1a2235;color:#94a3b8;border:1px solid #1f2d40;text-decoration:none">Jira Board</a></div></div>\n'
    )

# Inject into ops.html
html = html.replace('<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3" id=agrid></div>', 
                    f'<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3" id=agrid>{agent_html}</div>')
html = html.replace('<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3" id=pgrid></div>',
                    f'<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3" id=pgrid>{proj_html}</div>')

with open(OUT, 'w') as f:
    f.write(html)

size = os.path.getsize(OUT)
print(f'Done! Size: {size} bytes')
# Verify
c2 = open(OUT).read()
print('agrid populated:', 'font-weight:700' in c2 and 'RONY' in c2)
print('pgrid populated:', 'CryptoGyani' in c2)
print('Jira links:', 'IT-34' in c2)
