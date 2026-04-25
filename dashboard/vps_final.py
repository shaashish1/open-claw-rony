#!/usr/bin/env python3
"""Complete ops.html builder — run on VPS as: sudo python3 /tmp/vf.py"""
import json, os, urllib.request, base64

OUT = '/opt/itgyani-dashboard/frontend/ops.html'
J = 'https://itgyani.atlassian.net'

def jira_stats():
    try:
        tok = os.environ.get('JIRA_TOKEN','')
        em = os.environ.get('JIRA_EMAIL','')
        if not tok: return 41,0,0
        creds = base64.b64encode(f'{em}:{tok}'.encode()).decode()
        req = urllib.request.Request(
            f'{J}/rest/agile/1.0/board/7/issue?maxResults=50',
            headers={'Authorization':f'Basic {creds}','Accept':'application/json'})
        with urllib.request.urlopen(req,timeout=5) as r:
            d = json.loads(r.read())
        total=d.get('total',41)
        done=sum(1 for i in d.get('issues',[]) if i['fields']['status']['statusCategory']['key']=='done')
        prog=sum(1 for i in d.get('issues',[]) if i['fields']['status']['statusCategory']['key']=='indeterminate')
        return total,done,prog
    except Exception as e:
        print('Jira err:',e)
        return 41,0,0

total,done,prog = jira_stats()
pct = round(done/total*100) if total else 0

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

def ring(u, col):
    r=22; c=2*3.14159*r; off=c-(u/100)*c
    return (f'<svg style="transform:rotate(-90deg)" width=52 height=52 viewBox="0 0 52 52">'
            f'<circle fill=none stroke=#1f2d40 stroke-width=5 cx=26 cy=26 r={r}/>'
            f'<circle fill=none stroke-width=5 stroke-linecap=round cx=26 cy=26 r={r} stroke={col} '
            f'stroke-dasharray={c:.1f} stroke-dashoffset={off:.1f}/></svg>')

def badge(s):
    if s=='live': return '<span class=bdg style="background:#052e16;color:#4ade80;border:1px solid #166534">LIVE</span>'
    if s=='build': return '<span class=bdg style="background:#1c1917;color:#fb923c;border:1px solid #9a3412">BUILDING</span>'
    return '<span class=bdg style="background:#1e1b4b;color:#818cf8;border:1px solid #3730a3">PLANNED</span>'

def prio_badge(p):
    if p=='high': return '<span class=bdg style="background:#450a0a;color:#f87171;border:1px solid #991b1b">HIGH</span>'
    if p=='med': return '<span class=bdg style="background:#1c1917;color:#fbbf24;border:1px solid #92400e">MED</span>'
    return '<span class=bdg style="background:#111827;color:#6b7280;border:1px solid #374151">LOW</span>'

def dot(s):
    if s=='live': return '<span class=dt style="background:#4ade80;animation:P 2s infinite"></span>'
    if s=='build': return '<span class=dt style="background:#fb923c;animation:P 2s infinite"></span>'
    return '<span class=dt style="background:#818cf8"></span>'

def util_color(u):
    if u>=70: return '#4ade80'
    if u>=40: return '#fbbf24'
    return '#818cf8'

agent_cards = ''
for a in AGENTS:
    name,role,status,task,util,model,kpis,jira = a
    rc = util_color(util)
    kpi_html = ''.join(f'<div style=text-align:center><div style="font-size:.65rem;color:#6b7280;margin-bottom:2px">{k[1]}</div><div style="color:#e2e8f0;font-size:.85rem;font-weight:700">{k[0]}</div></div>' for k in kpis)
    jira_html = ''.join(f'<a href={J}/browse/{j[0]} target=_blank style="display:flex;align-items:center;gap:4px;text-decoration:none;margin-bottom:3px"><span style="color:#818cf8;font-family:monospace;font-size:.7rem;flex-shrink:0">{j[0]}</span><span style="color:#6b7280;font-size:.72rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:160px">{j[1]}</span></a>' for j in jira)
    agent_cards += (
        f'<div style="background:#1a2235;border:1px solid #1f2d40;border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:8px">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
        f'<div style="display:flex;align-items:center;gap:8px">{dot(status)}'
        f'<div><div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">'
        f'<span style="color:#fff;font-weight:700;font-size:.85rem">{name}</span>{badge(status)}</div>'
        f'<div style="color:#6b7280;font-size:.72rem">{role}</div></div></div>'
        f'<div style=position:relative;width:52px;height:52px;flex-shrink:0>{ring(util,rc)}'
        f'<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:700;color:{rc}">{util}%</div></div></div>'
        f'<div style="color:#6b7280;font-size:.75rem;line-height:1.5;border-left:2px solid #334155;padding-left:8px">{task}</div>'
        f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px;background:#0f172a60;border-radius:6px;padding:8px">{kpi_html}</div>'
        f'<div><div style="font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#374151;margin-bottom:4px">Jira Tickets</div>{jira_html}</div>'
        f'<div style="display:flex;justify-content:space-between;padding-top:6px;border-top:1px solid #1f2d40">'
        f'<span style="color:#4b5563;font-size:.7rem">Model: <span style=color:#6b7280>{model}</span></span>'
        f'<span style="font-size:.7rem;font-weight:700;color:{rc}">{util}% util</span></div></div>\n'
    )

proj_cards = ''
for p in PROJECTS:
    key,name,status,prio,desc,url,jurl,total_i,done_i,prog_i,owner,rev,miles = p
    pp = round(done_i/total_i*100) if total_i else 0
    miles_html = ''.join(f'<a href={J}/browse/{m[0]} target=_blank style="display:flex;align-items:center;gap:4px;text-decoration:none;margin-bottom:3px"><span style="color:#818cf8;font-family:monospace;font-size:.7rem;flex-shrink:0">{m[0]}</span><span style="color:#6b7280;font-size:.72rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{m[1]}</span></a>' for m in miles)
    live_btn = f'<a href={url} target=_blank style="flex:1;text-align:center;padding:5px;border-radius:6px;font-size:.78rem;font-weight:600;background:#1a2235;color:#94a3b8;border:1px solid #1f2d40;text-decoration:none">Live</a>' if url != '#' else ''
    proj_cards += (
        f'<div class=prc style="display:flex;flex-direction:column;gap:8px">'
        f'<div><div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:3px">'
        f'<span style="color:#fff;font-weight:700">{name}</span>{badge(status)}{prio_badge(prio)}</div>'
        f'<div style="color:#6b7280;font-size:.72rem">{desc}</div></div>'
        f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;text-align:center;background:#0f172a60;border-radius:6px;padding:8px">'
        f'<div><div style="color:#4ade80;font-weight:700;font-size:1.2rem">{done_i}</div><div style="color:#4b5563;font-size:.65rem">Done</div></div>'
        f'<div><div style="color:#fb923c;font-weight:700;font-size:1.2rem">{prog_i}</div><div style="color:#4b5563;font-size:.65rem">In Prog</div></div>'
        f'<div><div style="color:#e2e8f0;font-weight:700;font-size:1.2rem">{total_i-done_i-prog_i}</div><div style="color:#4b5563;font-size:.65rem">To Do</div></div></div>'
        f'<div class=pb><div class=pf style="width:{pp}%;background:linear-gradient(90deg,#16a34a,#4ade80)"></div></div>'
        f'<div style="display:flex;justify-content:space-between;font-size:.72rem;color:#6b7280"><span>{pp}% - {total_i} issues</span><span>{owner}</span></div>'
        f'<div style="font-size:.72rem;color:#6b7280">{rev}</div>'
        f'<div style="padding-top:6px;border-top:1px solid #1f2d40"><div style="font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#374151;margin-bottom:4px">Next Milestones</div>{miles_html}</div>'
        f'<div style="display:flex;gap:6px">{live_btn}'
        f'<a href={jurl} target=_blank style="flex:1;text-align:center;padding:5px;border-radius:6px;font-size:.78rem;font-weight:600;background:#1a2235;color:#94a3b8;border:1px solid #1f2d40;text-decoration:none">Jira Board</a></div></div>\n'
    )

JS = r"""
const S={ma:null,mp:1,mu:null};let logs=[];let cd=30;
function tab(n,el){document.querySelectorAll('.tp').forEach(t=>t.classList.add('hidden'));document.querySelectorAll('.nt').forEach(t=>t.classList.remove('on'));document.getElementById('tp-'+n).classList.remove('hidden');if(el)el.classList.add('on');if(n==='mailbox')initMail();if(n==='sprint')loadSprint();if(n==='systems')loadSys();}
function tick(){var el=document.getElementById('clk');if(el)el.textContent=new Date().toLocaleTimeString('en-IN',{timeZone:'Asia/Calcutta',hour12:true});}
setInterval(tick,1000);tick();
async function initMail(){try{var r=await fetch('/api/accounts');if(r.status===401||r.status===403){showML();return;}var a=await r.json();if(!Array.isArray(a)){showML();return;}renderAccts(a);if(a.length>0&&!S.ma)selAcct(a[0].email,a[0].label);}catch(e){showML();}}
function showML(){document.getElementById('alist').innerHTML='<div style="color:#6b7280;font-size:.78rem;padding:8px">Login required</div>';document.getElementById('elist').innerHTML='';document.getElementById('remp').classList.remove('hidden');document.getElementById('rcont').classList.add('hidden');document.getElementById('mlogin').classList.remove('hidden');}
async function mailLogin(){var fd=new FormData();fd.append('username',document.getElementById('mlu').value);fd.append('password',document.getElementById('mlp').value);document.getElementById('mlerr').classList.add('hidden');try{await fetch('/login',{method:'POST',body:fd,redirect:'follow'});var r=await fetch('/api/accounts');if(r.ok){document.getElementById('mlogin').classList.add('hidden');var a=await r.json();renderAccts(a);if(a.length>0)selAcct(a[0].email,a[0].label);addLog('Mailbox unlocked','g');}else{document.getElementById('mlerr').classList.remove('hidden');}}catch(e){document.getElementById('mlerr').classList.remove('hidden');}}
function renderAccts(a){var el=document.getElementById('alist');el.innerHTML='';a.forEach(function(x){var u=x.unread||0;el.innerHTML+='<div class="ai flex items-center justify-between" data-email="'+x.email+'" onclick="selAcct(\''+x.email+'\',\''+(x.label||x.email)+'\')">'+'<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+(x.label||x.email.split('@')[0])+'</span>'+(u>0?'<span style="font-size:.7rem;background:#312e81;color:#a5b4fc;padding:1px 6px;border-radius:8px;flex-shrink:0">'+(u>99?'99+':u)+'</span>':'')+'</div>';});}
async function selAcct(email,label){S.ma=email;S.mp=1;S.mu=null;document.getElementById('ilbl').textContent=(label||email).toUpperCase();document.querySelectorAll('.ai').forEach(function(el){el.classList.toggle('on',el.dataset.email===email);});await loadEmails();}
async function loadEmails(){if(!S.ma)return;var el=document.getElementById('elist');el.innerHTML='<div style="color:#6b7280;font-size:.78rem;padding:16px;text-align:center"><span class=sp></span></div>';try{var r=await fetch('/api/emails?account='+encodeURIComponent(S.ma)+'&page='+S.mp+'&limit=20');if(r.status===401){showML();return;}var d=await r.json();var emails=d.emails||[];el.innerHTML='';if(!emails.length){el.innerHTML='<div style="color:#6b7280;font-size:.78rem;padding:16px;text-align:center">No emails</div>';return;}emails.forEach(function(e){var from=(e.from_addr||'').replace(/<[^>]+>/g,'').trim().split('@')[0].substring(0,18);var subj=(e.subject||'(no subject)').substring(0,40);var date=e.date_str?e.date_str.substring(0,10):'';el.innerHTML+='<div class="er'+((!e.is_read)?' ur':'')+'" onclick="openEmail(\''+(e.uid||e.id)+'\')">'+'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:2px">'+'<span style="color:#cbd5e1;font-size:.75rem;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+from+'</span>'+'<span style="color:#4b5563;font-size:.7rem;flex-shrink:0">'+date+'</span></div>'+'<div class=es style="color:#6b7280;font-size:.75rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+subj+'</div></div>';});}catch(e){el.innerHTML='<div style="color:#f87171;font-size:.78rem;padding:12px">Error: '+e.message+'</div>';}}
async function openEmail(uid){S.mu=uid;document.getElementById('remp').classList.add('hidden');document.getElementById('mlogin').classList.add('hidden');document.getElementById('rcont').classList.remove('hidden');document.getElementById('rsub').textContent='Loading...';document.getElementById('rbody').innerHTML='<span class=sp></span>';cancelReply();try{var r=await fetch('/api/emails/'+encodeURIComponent(S.ma)+'/'+uid);var d=await r.json();var e=d.email||d;document.getElementById('rsub').textContent=e.subject||'(no subject)';document.getElementById('rmeta').textContent='From: '+(e.from_addr||'')+' | '+(e.date_str||'');if(e.body_html){document.getElementById('rbody').innerHTML='<iframe srcdoc="'+e.body_html.replace(/"/g,'&quot;')+'" style="width:100%;height:280px;border:none;background:#fff;border-radius:4px"></iframe>';}else{document.getElementById('rbody').textContent=e.body_text||'(empty)';}}catch(e){document.getElementById('rbody').textContent='Failed: '+e.message;}}
function showReply(){document.getElementById('rarea').classList.remove('hidden');document.getElementById('rbtns').classList.add('hidden');document.getElementById('rtxt').focus();}
function cancelReply(){document.getElementById('rarea').classList.add('hidden');document.getElementById('rbtns').classList.remove('hidden');document.getElementById('rtxt').value='';}
async function sendReply(){var txt=document.getElementById('rtxt').value.trim();if(!txt||!confirm('Send this reply?'))return;try{await fetch('/api/emails/'+encodeURIComponent(S.ma)+'/'+S.mu+'/send-reply',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({reply_text:txt})});cancelReply();addLog('Reply sent','g');alert('Sent!');}catch(e){alert('Failed: '+e.message);}}
async function deleteEmail(){if(!confirm('Move to Trash?'))return;try{await fetch('/api/emails/'+encodeURIComponent(S.ma)+'/'+S.mu,{method:'DELETE'});document.getElementById('remp').classList.remove('hidden');document.getElementById('rcont').classList.add('hidden');loadEmails();addLog('Email deleted','o');}catch(e){alert('Delete failed: '+e.message);}}
function mailPage(d){S.mp=Math.max(1,S.mp+d);loadEmails();}
async function syncEmail(){try{await fetch('/api/sync/quick',{method:'POST'});addLog('Email sync triggered','b');setTimeout(function(){if(S.ma)loadEmails();},3000);}catch(e){}}
function getTasks(){try{return JSON.parse(localStorage.getItem('ig_tasks')||'[]');}catch(e){return [];}}
function saveTasks(t){localStorage.setItem('ig_tasks',JSON.stringify(t));}
function addTask(){var ti=document.getElementById('ttl').value.trim();if(!ti)return;var tasks=getTasks();tasks.unshift({id:Date.now(),title:ti,agent:document.getElementById('tagt').value,prio:document.getElementById('tpri').value,status:'todo',created:new Date().toISOString()});saveTasks(tasks);document.getElementById('ttl').value='';renderTasks();addLog('Task -> '+document.getElementById('tagt').value+': '+ti,'b');}
function cycleTask(id){var tasks=getTasks();var t=tasks.find(function(x){return x.id===id;});if(!t)return;var seq=['todo','doing','done'];t.status=seq[(seq.indexOf(t.status)+1)%seq.length];saveTasks(tasks);renderTasks();}
function delTask(id){saveTasks(getTasks().filter(function(x){return x.id!==id;}));renderTasks();}
function renderTasks(){var tasks=getTasks();var cols={todo:[],doing:[],done:[]};tasks.forEach(function(t){if(cols[t.status])cols[t.status].push(t);});[['todo','ctd','ctodo'],['doing','cdg','cdoing'],['done','cdn','cdone']].forEach(function(x){var col=document.getElementById(x[2]);var cnt=document.getElementById(x[0]);if(cnt)cnt.textContent=cols[x[0]].length;if(!col)return;if(!cols[x[0]].length){col.innerHTML='<div style="color:#374151;font-size:.75rem;text-align:center;padding:16px">Empty</div>';return;}col.innerHTML=cols[x[0]].map(function(t){var pc=t.prio==='high'?'background:#450a0a;color:#f87171;border:1px solid #991b1b':t.prio==='med'?'background:#1c1917;color:#fbbf24;border:1px solid #92400e':'background:#111827;color:#6b7280;border:1px solid #374151';return '<div class="tc'+(x[0]==='done'?' dn':'')+'" onclick="cycleTask('+t.id+')">'+'<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:4px;margin-bottom:4px">'+'<span style="color:#e2e8f0;font-size:.85rem;font-weight:500">'+t.title+'</span>'+'<button style="color:#4b5563;cursor:pointer;border:none;background:none;flex-shrink:0;font-size:1rem" onclick="event.stopPropagation();delTask('+t.id+')">x</button></div>'+'<div style="display:flex;align-items:center;gap:6px"><span style="color:#818cf8;font-size:.72rem">'+t.agent+'</span><span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;'+pc+'">'+t.prio+'</span></div></div>';}).join('');});}
async function loadSprint(){try{var r=await fetch('/api/ops/jira-sprint',{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);var d=await r.json();var dn=d.done||0,tot=