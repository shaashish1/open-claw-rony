
# This script finishes building ops.html on VPS
# Run: python3 /tmp/finish_ops.py

RAVI_DATA = ("RAVI","RevOps / Payments","live","Razorpay + Stripe integration across all 7 properties",15,"Haiku",
   [("0/7","Properties Live"),("Pending","Razorpay"),("Pending","Stripe")],
   [("IT-10","Payment system setup"),("IT-41","Pricing Rs999 payment")])

AGENTS = [
  ("RONY","COO","live","Sprint oversight + agent coordination + blocker escalation",72,"Sonnet",
   [("10/14","Agents Active"),("0/41","Sprint Done"),("0","Blockers")],
   [("IT-34","Agent KPI tiles on dashboard"),("IT-35","QA all dashboard panels")]),
  ("MAYA","CMO / Lead Gen","live","Email cleanup 8031 emails + 1M lead database build",45,"Haiku",
   [("0/8031","Emails Scanned"),("0/50K","Leads Built"),("0","Campaigns")],
   [("IT-26","Audit 8031 emails"),("IT-27","Email cleanup n8n"),("IT-28","Lead scraper 50K"),("IT-30","SendGrid setup"),("IT-31","First 50K campaign")]),
  ("ARJUN","InfoSec","build","Security audit + job alert bot VPS deploy + RULE 0",30,"Sonnet",
   [("Clean","Secrets Status"),("0","Alerts Fired"),("0","Violations")],
   [("YUKTI-7","Security audit OpenAlgo"),("IT-38","Job scraper multi-portal")]),
  ("PRIYA","SEO Lead","live","CryptoGyani SEO launch - 10 articles/week",55,"Haiku",
   [("0/10","Articles Published"),("0/100","Keywords Mapped"),("Pending","AdSense")],
   [("CG-52","CryptoGyani SEO Launch"),("CG-55","GA4 Search Console"),("CG-56","10 SEO articles"),("CG-59","Apply AdSense")]),
  ("ZARA","Sales","live","100 cold email prospects - fintech and SaaS founders",20,"Haiku",
   [("0/100","Prospects Found"),("0","Emails Sent"),("0","Replies Got")],
   [("IT-15","First 5 agency clients"),("IT-21","Cold email 100 prospects"),("IT-23","LinkedIn 50 DMs/day")]),
  ("FELIX","Support","plan","50-FAQ SOP library + support bot setup",5,"Haiku",
   [("0/50","FAQs Written"),("Not live","Support Bot"),("0","Open Tickets")],
   [("IT-11","Customer support bot")]),
  ("DISHA","PM","live","Sprint 1 daily standup + blocker escalation within 30 min",40,"Haiku",
   [("0","Blockers"),("N/A","On-time"),("At Risk","Sprint Health")],
   [("IT-1","Sprint 1 kickoff"),("IT-12","Admin dashboard"),("IT-13","Automation test")]),
  ("KABIR","DevOps","live","VPS hardening + Fyers auto-login + n8n YouTube production",85,"Haiku",
   [("10/10","Strategies Up"),("99.9%","VPS Uptime"),("16%","Disk Used")],
   [("YUKTI-3","Audit OpenAlgo VPS"),("YUKTI-4","Document broker config"),("IT-13","Automation test")]),
  ("NIKKI","Designer / QA","build","ITGYANI service page + QA gate for all UI",35,"Haiku",
   [("Active","QA Gate"),("0/3","Pages Done"),("0","Bugs Found")],
   [("IT-20","Service menu pricing page"),("IT-4","Design service categories")]),
  ("VIKRAM","Analytics","live","Revenue KPI + daily P&L + ad performance",50,"Haiku",
   [("Rs 0","Revenue MTD"),("N/A","Ad ROAS"),("0/7","Reports Done")],
   [("IT-33","AI model costs panel"),("IT-36","Dashboard load test"),("YUKTI-6","P&L integration")]),
  ("ROHAN","Finance","live","Revenue tracking + cost monitoring + burn rate",20,"Haiku",
   [("Rs 0","Revenue"),("Calculating","Burn Rate"),("Unknown","Runway")],
   [("IT-10","Payment system setup")]),
  ("TARA","Research","live","Demand validation: Job App + OpenMAIC courses",30,"Haiku",
   [("0/3","Products Validated"),("N/A","Score"),("0/5","Market Reports")],
   [("IT-37","Demand landing page"),("IT-5","Research pain points")]),
  ("KIRAN","HR & Team Ops","plan","14-agent RACI + onboarding SOP + roster",5,"Haiku",
   [("Pending","RACI Matrix"),("14/14","Agents Onboarded"),("0/5","SOPs Written")],
   [("IT-6","Onboarding form")]),
  ("RAVI","RevOps / Payments","live","Razorpay + Stripe across all 7 properties - 7 days",15,"Haiku",
   [("0/7","Properties Live"),("Pending","Razorpay"),("Pending","Stripe")],
   [("IT-10","Payment setup"),("IT-41","Rs999 payment integration")]),
]

PROJECTS = [
  ("IT","ITGYANI Agency","active","high","AI automation agency - first 5 clients, service page, cold outreach",
   "https://itgyani.com","https://itgyani.atlassian.net/jira/software/projects/IT/boards/7",
   41,0,0,"RONY/ZARA","Rs 0 to Rs 1L/mo",
   [("IT-15","First 5 clients"),("IT-20","Service page live"),("IT-21","100 cold emails")]),
  ("CG","CryptoGyani.com","active","high","SEO crypto blog + AdSense + newsletter - passive income",
   "https://cryptogyani.com","https://itgyani.atlassian.net/jira/software/projects/CG/boards",
   54,4,0,"PRIYA","Rs 0 to AdSense passive",
   [("CG-52","SEO launch"),("CG-56","10 articles"),("CG-59","AdSense apply")]),
  ("YUKTI","Yukti Algo Trading","active","high","OpenAlgo algo trading SaaS - 10 strategies live analyze mode",
   "https://openalgo.cryptogyani.com","https://itgyani.atlassian.net/jira/software/projects/YUKTI/boards",
   7,0,0,"KABIR/VIKRAM","Paper Rs 1Cr to SaaS beta",
   [("YUKTI-3","VPS audit"),("YUKTI-5","Trading dashboard"),("YUKTI-6","P&L integration")]),
  ("TEF","The Employee Factory","active","med","OpenMAIC LMS - HR and career courses",
   "https://learn.theemployeefactory.com","https://itgyani.atlassian.net/jira/software/projects/TEF/boards",
   21,0,1,"TARA/FELIX","Rs 0 to course revenue",
   [("TEF-15","LMS go-live"),("TEF-16","First course"),("TEF-17","OpenMAIC live")]),
  ("KO","Kharadi Online","active","low","Self-hosted e-commerce - Amazon affiliate + local store",
   "https://kharadionline.com","https://itgyani.atlassian.net/jira/software/projects/KO/boards",
   5,0,0,"RAVI","Amazon affiliate ROAS 2x",
   [("KO-13","ROAS 2x campaign"),("KO-12","Amazon affiliate"),("KO-11","Amazon store sync")]),
  ("ARJUN_BOT","AI Job Alert App","build","med","Job_Alert_Rony_Bot - LinkedIn scraper AI scoring Telegram alerts",
   "https://t.me/Job_Alert_Rony_Bot","https://itgyani.atlassian.net/jira/software/projects/IT/boards/7",
   6,0,1,"ARJUN","Rs 999/mo subscription",
   [("IT-37","Demand validation"),("IT-38","Multi-portal scraper"),("IT-42","Beta 10 users")]),
  ("QPF","QuickPay Finance","plan","low","India crypto exchange + FIAT gateway + DEX - future property",
   "#","https://itgyani.atlassian.net/jira/software/projects/QPF/boards",
   3,0,0,"TARA (validation)","Long-term SaaS",
   [("QPF-1","India exchange"),("QPF-2","On/Off ramp"),("QPF-3","DEX")]),
  ("SF","SendMoney Finance","plan","low","International money transfer + stablecoin INRT",
   "#","https://itgyani.atlassian.net/jira/software/projects/SF/boards",
   7,0,0,"TARA (validation)","Long-term fintech",
   [("SF-1","Landing branding"),("SF-6","Stable coin INRT"),("SF-2","KYC dashboard")]),
]

def agent_js(agents):
    items = []
    for a in agents:
        name,role,status,task,util,model,kpis,jira = a
        kpi_json = str([[k[0],k[1]] for k in kpis]).replace("'",'"')
        jira_json = str([[j[0],j[1]] for j in jira]).replace("'",'"')
        items.append('{name:"%s",role:"%s",status:"%s",task:"%s",util:%d,model:"%s",kpis:%s,jira:%s}' % (
            name,role,status,task,util,model,kpi_json,jira_json))
    return "const AGENTS=[%s];" % ",".join(items)

def proj_js(projects):
    items = []
    for p in projects:
        key,name,status,prio,desc,url,jurl,total,done,prog,owner,rev,miles = p
        miles_json = str([[m[0],m[1]] for m in miles]).replace("'",'"')
        items.append('{key:"%s",name:"%s",status:"%s",prio:"%s",desc:"%s",url:"%s",jurl:"%s",total:%d,done:%d,prog:%d,owner:"%s",rev:"%s",miles:%s}' % (
            key,name,status,prio,desc,url,jurl,total,done,prog,owner,rev,miles_json))
    return "const PROJECTS=[%s];" % ",".join(items)

js_data = agent_js(AGENTS) + "\n" + proj_js(PROJECTS)

JS_LOGIC = """
const S={mailAcct:null,mailPage:1,mailUid:null};
let logs=[];let cdTimer=30;

function tab(name,el){
  document.querySelectorAll('.tp').forEach(t=>t.classList.add('hidden'));
  document.querySelectorAll('.nav-tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tp-'+name).classList.remove('hidden');
  if(el)el.classList.add('active');
  if(name==='mailbox')initMailbox();
  if(name==='sprint')loadSprint();
  if(name==='systems')loadSystems();
}

function tick(){const el=document.getElementById('clock');if(el)el.textContent=new Date().toLocaleTimeString('en-IN',{timeZone:'Asia/Calcutta',hour12:true});}
setInterval(tick,1000);tick();

function ring(pct,col){
  const r=22,c=2*Math.PI*r,off=c-(pct/100)*c;
  return '<svg class="ring-svg" width="52" height="52" viewBox="0 0 52 52"><circle class="ring-bg" cx="26" cy="26" r="'+r+'"/><circle class="ring-fg" cx="26" cy="26" r="'+r+'" stroke="'+col+'" stroke-dasharray="'+c+'" stroke-dashoffset="'+off+'"/></svg>';
}

function renderAgents(){
  const g=document.getElementById('agents-grid');
  if(!g)return;
  g.innerHTML='';
  AGENTS.forEach(function(a){
    const sc=a.status==='live'?'b-live':a.status==='build'?'b-build':'b-plan';
    const dc=a.status==='live'?'dot-g pulse':a.status==='build'?'dot-o pulse':'dot-b';
    const sl=a.status==='live'?'LIVE':a.status==='build'?'BUILDING':'PLANNED';
    const rc=a.util>=70?'#4ade80':a.util>=40?'#fbbf24':'#818cf8';
    const uc=a.util>=70?'text-green-400':a.util>=40?'text-yellow-400':'text-indigo-400';
    const kpiHtml=a.kpis.map(function(k){return '<div class="text-center"><div class="text-slate-500 text-xs mb-0.5">'+k[1]+'</div><div class="text-white text-sm font-bold">'+k[0]+'</div></div>';}).join('');
    const jiraHtml=a.jira.map(function(j){return '<a href="https://itgyani.atlassian.net/browse/'+j[0]+'" target="_blank" class="flex items-center gap-1 hover:text-indigo-300"><span class="text-indigo-500 font-mono text-xs shrink-0">'+j[0]+'</span><span class="truncate text-xs" style="max-width:155px">'+j[1]+'</span></a>';}).join('');
    g.innerHTML+='<div class="card2 p-3 border border-transparent hover:border-slate-600 flex flex-col gap-2"><div class="flex items-start justify-between"><div class="flex items-center gap-2"><span class="dot '+dc+' mt-0.5"></span><div><div class="flex items-center gap-1.5"><span class="text-white font-bold text-sm">'+a.name+'</span><span class="badge '+sc+'">'+sl+'</span></div><div class="text-slate-500 text-xs">'+a.role+'</div></div></div><div class="ring-wrap">'+ring(a.util,rc)+'<div class="ring-lbl '+uc+'">'+a.util+'%</div></div></div><div class="text-slate-400 text-xs leading-relaxed border-l-2 border-slate-700 pl-2">'+a.task+'</div><div class="grid grid-cols-3 gap-1 bg-slate-900/40 rounded p-2">'+kpiHtml+'</div><div class="space-y-1"><div class="text-slate-600 text-xs font-semibold uppercase tracking-wider">Jira Tickets</div><div class="space-y-0.5 text-slate-400">'+jiraHtml+'</div></div><div class="flex items-center justify-between pt-1 border-t border-slate-800"><span class="text-slate-600 text-xs">Model: <span class="text-slate-400">'+a.model+'</span></span><span class="'+uc+' text-xs font-semibold">'+a.util+'% util</span></div></div>';
  });
}

function renderProjects(){
  const g=document.getElementById('projects-grid');
  if(!g)return;
  g.innerHTML='';
  PROJECTS.forEach(function(p){
    const pct=p.total>0?Math.round(p.done/p.total*100):0;
    const sc=p.status==='active'?'b-live':p.status==='build'?'b-build':'b-plan';
    const sl=p.status==='active'?'ACTIVE':p.status==='build'?'BUILDING':'PLANNED';
    const pc=p.prio==='high'?'b-hi':p.prio==='med'?'b-med':'b-lo';
    const mHtml=p.miles.map(function(m){return '<a href="https://itgyani.atlassian.net/browse/'+m[0]+'" target="_blank" class="flex items-center gap-1 text-slate-400 hover:text-indigo-300 text-xs"><span class="text-indigo-500 font-mono shrink-0">'+m[0]+'</span><span class="truncate">'+m[1]+'</span></a>';}).join('');
    const liveBtn=p.url!=='#'?'<a href="'+p.url+'" target="_blank" class="btn btn-g text-xs flex-1 text-center">Live</a>':'';
    g.innerHTML+='<div class="proj-card flex flex-col gap-2"><div class="flex items-start justify-between mb-1"><div><div class="flex items-center gap-1.5 flex-wrap mb-0.5"><span class="text-white font-bold">'+p.name+'</span><span class="badge '+sc+'">'+sl+'</span><span class="badge '+pc+'">'+p.prio.toUpperCase()+'</span></div><div class="text-slate-500 text-xs">'+p.desc+'</div></div></div><div class="grid grid-cols-3 gap-2 text-center bg-slate-900/30 rounded p-2"><div><div class="text-green-400 font-bold text-lg">'+p.done+'</div><div class="text-slate-600 text-xs">Done</div></div><div><div class="text-orange-400 font-bold text-lg">'+p.prog+'</div><div class="text-slate-600 text-xs">In Progress</div></div><div><div class="text-slate-300 font-bold text-lg">'+(p.total-p.done-p.prog)+'</div><div class="text-slate-600 text-xs">To Do</div></div></div><div class="pb"><div class="pf pf-g" style="width:'+pct+'%"></div></div><div class="flex items-center justify-between text-xs text-slate-500"><span>'+pct+'% - '+p.total+' issues</span><span>'+p.owner+'</span></div><div class="text-xs text-slate-500">'+p.rev+'</div><div class="space-y-0.5 pt-1 border-t border-slate-800"><div class="text-slate-600 text-xs font-semibold uppercase tracking-wider mb-1">Next Milestones</div>'+mHtml+'</div><div class="flex gap-1 pt-1">'+liveBtn+'<a href="'+p.jurl+'" target="_blank" class="btn btn-g text-xs flex-1 text-center">Jira Board</a></div></div>';
  });
}

async function initMailbox(){
  try{
    const r=await fetch('/api/accounts');
    if(r.status===401||r.status===403){showMailLogin();return;}
    const accounts=await r.json();
    if(!Array.isArray(accounts)){showMailLogin();return;}
    renderAccounts(accounts);
    if(accounts.length>0&&!S.mailAcct)selectAccount(accounts[0].email,accounts[0].label);
  }catch(e){showMailLogin();}
}
function showMailLogin(){
  document.getElementById('acct-list').innerHTML='<div class="text-slate-500 text-xs p-2">Login required</div>';
  document.getElementById('email-list').innerHTML='';
  document.getElementById('reader-empty').classList.add('hidden');
  document.getElementById('reader-content').classList.add('hidden');
  document.getElementById('mail-login-prompt').classList.remove('hidden');
}
async function mailLogin(){
  const fd=new FormData();
  fd.append('username',document.getElementById('ml-user').value);
  fd.append('password',document.getElementById('ml-pass').value);
  document.getElementById('ml-err').classList.add('hidden');
  try{
    await fetch('/login',{method:'POST',body:fd,redirect:'follow'});
    const r=await fetch('/api/accounts');
    if(r.ok){
      document.getElementById('mail-login-prompt').classList.add('hidden');
      const a=await r.json();renderAccounts(a);
      if(a.length>0)selectAccount(a[0].email,a[0].label);
      addLog('Mailbox unlocked','g');
    }else{document.getElementById('ml-err').classList.remove('hidden');}
  }catch{document.getElementById('ml-err').classList.remove('hidden');}
}
function renderAccounts(accounts){
  const el=document.getElementById('acct-list');el.innerHTML='';
  accounts.forEach(function(a){
    const u=a.unread||0;
    el.innerHTML+='<div class="acc-item flex items-center justify-between" data-email="'+a.email+'" onclick="selectAccount(\''+a.email+'\',\''+( a.label||a.email)+'\')">' +
      '<span class="truncate">'+(a.label||a.email.split('@')[0])+'</span>'+
      (u>0?'<span class="text-xs bg-indigo-900 text-indigo-300 px-1.5 rounded-full shrink-0">'+(u>99?'99+':u)+'</span>':'')+'</div>';
  });
}
async function selectAccount(email,label){
  S.mailAcct=email;S.mailPage=1;S.mailUid=null;
  document.getElementById('inbox-label').textContent=(label||email).toUpperCase();
  document.querySelectorAll('.acc-item').forEach(function(el){el.classList.toggle('active',el.dataset.email===email);});
  await loadEmails();
}
async function loadEmails(){
  if(!S.mailAcct)return;
  const el=document.getElementById('email-list');
  el.innerHTML='<div class="text-slate-500 text-xs p-4 text-center"><span class="spin"></span></div>';
  try{
    const r=await fetch('/api/emails?account='+encodeURIComponent(S.mailAcct)+'&page='+S.mailPage+'&limit=20');
    if(r.status===401){showMailLogin();return;}
    const d=await r.json();const emails=d.emails||[];
    el.innerHTML='';
    if(!emails.length){el.innerHTML='<div class="text-slate-500 text-xs p-4 text-center">No emails</div>';return;}
    emails.forEach(function(e){
      const from=(e.from_addr||'').replace(/<[^>]+>/g,'').trim().split('@')[0].substring(0,18);
      const subj=(e.subject||'(no subject)').substring(0,40);
      const date=e.date_str?e.date_str.substring(0,10):'';
      el.innerHTML+='<div class="email-row '+((!e.is_read)?'unread':'')+'" onclick="openEmail(\\''+( e.uid||e.id)+'\\')"><div class="flex items-center justify-between mb-0.5"><span class="text-slate-300 text-xs font-semibold truncate">'+from+'</span><span class="text-slate-600 text-xs shrink-0">'+date+'</span></div><div class="e-subj text-slate-400 text-xs truncate">'+subj+'</div></div>';
    });
  }catch(e){el.innerHTML='<div class="text-red-400 text-xs p-3">Error: '+e.message+'</div>';}
}
async function openEmail(uid){
  S.mailUid=uid;
  document.getElementById('reader-empty').classList.add('hidden');
  document.getElementById('mail-login-prompt').classList.add('hidden');
  document.getElementById('reader-content').classList.remove('hidden');
  document.getElementById('r-subject').textContent='Loading...';
  document.getElementById('r-body').innerHTML='<span class="spin"></span>';
  cancelReply();
  try{
    const r=await fetch('/api/emails/'+encodeURIComponent(S.mailAcct)+'/'+uid);
    const d=await r.json();const e=d.email||d;
    document.getElementById('r-subject').textContent=e.subject||'(no subject)';
    document.getElementById('r-meta').textContent='From: '+(e.from_addr||'')+' | '+(e.date_str||'');
    if(e.body_html){
      document.getElementById('r-body').innerHTML='<iframe srcdoc="'+e.body_html.replace(/"/g,'&quot;')+'" style="width:100%;height:280px;border:none;background:#fff;border-radius:4px"></iframe>';
    }else{document.getElementById('r-body').textContent=e.body_text||'(empty)';}
  }catch(e){document.getElementById('r-body').textContent='Failed: '+e.message;}
}
function showReply(){document.getElementById('reply-area').classList.remove('hidden');document.getElementById('reply-btns').classList.add('hidden');document.getElementById('reply-txt').focus();}
function cancelReply(){document.getElementById('reply-area').classList.add('hidden');document.getElementById('reply-btns').classList.remove('hidden');document.getElementById('reply-txt').value='';}
async function sendReply(){
  const txt=document.getElementById('reply-txt').value.trim();
  if(!txt||!confirm('Send this reply?'))return;
  try{
    await fetch('/api/emails/'+encodeURIComponent(S.mailAcct)+'/'+S.mailUid+'/send-reply',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({reply_text:txt})});
    cancelReply();addLog('Reply sent from '+S.mailAcct,'g');alert('Sent!');
  }catch(e){alert('Failed: '+e.message);}
}
async function deleteEmail(){
  if(!confirm('Move to Trash?'))return;
  try{
    await fetch('/api/emails/'+encodeURIComponent(S.mailAcct)+'/'+S.mailUid,{method:'DELETE'});
    document.getElementById('reader-empty').classList.remove('hidden');
    document.getElementById('reader-content').classList.add('hidden');
    loadEmails();addLog('Email deleted','o');
  }catch(e){alert('Delete failed: '+e.message);}
}
function mailPage(d){S.mailPage=Math.max(1,S.mailPage+d);loadEmails();}
async function syncEmail(){
  try{await fetch('/api/sync/quick',{method:'POST'});addLog('Email sync triggered','b');setTimeout(function(){if(S.mailAcct)loadEmails();},3000);}catch{}
}

function getTasks(){try{return JSON.parse(localStorage.getItem('ig_tasks')||'[]');}catch{return [];}}
function saveTasks(t){localStorage.setItem('ig_tasks',JSON.stringify(t));}
function addTask(){
  const title=document.getElementById('t-title').value.trim();
  if(!title)return;
  const tasks=getTasks();
  tasks.unshift({id:Date.now(),title:title,agent:document.getElementById('t-agent').value,prio:document.getElementById('t-prio').value,status:'todo',created:new Date().toISOString()});
  saveTasks(tasks);document.getElementById('t-title').value='';renderTasks();
  addLog('Task -> '+document.getElementById('t-agent').value+': '+title,'b');
}
function cycleTask(id){const tasks=getTasks();const t=tasks.find(function(x){return x.id===id;});if(!t)return;const seq=['todo','doing','done'];t.status=seq[(seq.indexOf(t.status)+1)%seq.length];saveTasks(tasks);renderTasks();}
function delTask(id){saveTasks(getTasks().filter(function(x){return x.id!==id;}));renderTasks();}
function renderTasks(){
  const tasks=getTasks();
  const cols={todo:[],doing:[],done:[]};
  tasks.forEach(function(t){if(cols[t.status])cols[t.status].push(t);});
  ['todo','doing','done'].forEach(function(st){
    const col=document.getElementById('col-'+st);
    const cnt=document.getElementById('cnt-'+st);
    if(cnt)cnt.textContent=cols[st].length;
    if(!col)return;
    if(!cols[st].length){col.innerHTML='<div class="text-slate-700 text-xs text-center py-4">Empty</div>';return;}
    col.innerHTML=cols[st].map(function(t){
      const pc=t.prio==='high'?'b-hi':t.prio==='med'?'b-med':'b-lo';
      return '<div class="task-card'+(st==='done'?' done-card':'')+'" onclick="cycleTask('+t.id+')">' +
        '<div class="flex items-start justify-between gap-1 mb-1"><span class="text-slate-200 text-sm font-medium">'+t.title+'</span>' +
        '<button class="text-slate-600 hover:text-red-400 shrink-0" onclick="event.stopPropagation();delTask('+t.id+')">x</button></div>' +
        '<div class="flex items-center gap-1.5"><span class="text-indigo-400 text-xs">'+t.agent+'</span><span class="badge '+pc+'">'+t.prio+'</span></div></div>';
    }).join('');
  });
}

async function loadSprint(){
  try{
    const r=await fetch('/api/ops/jira-sprint',{cache:'no-store'});
    if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();
    const done=d.done||0,total=d.total||0,inp=d.in_progress||0;
    document.getElementById('k-j').textContent=done+'/'+total;
    document.getElementById('k-j-l').textContent='Done of '+total+' issues';
    document.getElementById('k-j-b').style.width=(total>0?(done/total*100):0)+'%';
    document.getElementById('sprint-meta').textContent=total+' issues - '+done+' done - '+inp+' in progress - '+(total-done-inp)+' to do';
    const jt=document.getElementById('j-todo'),jp=document.getElementById('j-prog'),jd=document.getElementById('j-done');
    jt.innerHTML='';jp.innerHTML='';jd.innerHTML='';
    (d.issues||[]).forEach(function(i){
      const cat=i.status