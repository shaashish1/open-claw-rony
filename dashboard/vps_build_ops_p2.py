#!/usr/bin/env python3
"""Part 2: append JS to ops.html. Run AFTER vps_build_ops.py"""
import json, os

JIRA = 'https://itgyani.atlassian.net'
OUT = '/opt/itgyani-dashboard/frontend/ops.html'

projects = [
    ["IT","ITGYANI Agency","active","high","AI automation agency - first 5 clients service page cold outreach",
     "https://itgyani.com",JIRA+"/jira/software/projects/IT/boards/7",41,0,0,"RONY/ZARA","Rs 0 to Rs 1L/mo",
     [["IT-15","First 5 clients"],["IT-20","Service page live"],["IT-21","100 cold emails"]]],
    ["CG","CryptoGyani.com","active","high","SEO crypto blog + AdSense + newsletter - passive income engine",
     "https://cryptogyani.com",JIRA+"/jira/software/projects/CG/boards",54,4,0,"PRIYA","Rs 0 to AdSense passive",
     [["CG-52","SEO launch"],["CG-56","10 articles"],["CG-59","AdSense apply"]]],
    ["YUKTI","Yukti Algo Trading","active","high","OpenAlgo algo trading SaaS - 10 strategies live analyze mode",
     "https://openalgo.cryptogyani.com",JIRA+"/jira/software/projects/YUKTI/boards",7,0,0,"KABIR/VIKRAM","Paper Rs 1Cr to SaaS beta",
     [["YUKTI-3","VPS audit"],["YUKTI-5","Trading dashboard"],["YUKTI-6","P&L integration"]]],
    ["TEF","The Employee Factory","active","med","OpenMAIC LMS - HR and career courses",
     "https://learn.theemployeefactory.com",JIRA+"/jira/software/projects/TEF/boards",21,0,1,"TARA/FELIX","Rs 0 to course revenue",
     [["TEF-15","LMS go-live"],["TEF-16","First course"],["TEF-17","OpenMAIC live"]]],
    ["KO","Kharadi Online","active","low","Self-hosted e-commerce - Amazon affiliate + local store scanner",
     "https://kharadionline.com",JIRA+"/jira/software/projects/KO/boards",5,0,0,"RAVI","Amazon affiliate ROAS 2x",
     [["KO-13","ROAS 2x campaign"],["KO-12","Amazon affiliate"],["KO-11","Amazon store sync"]]],
    ["JOB","AI Job Alert App","build","med","Job_Alert_Rony_Bot - LinkedIn scraper AI scoring Telegram alerts",
     "https://t.me/Job_Alert_Rony_Bot",JIRA+"/jira/software/projects/IT/boards/7",6,0,1,"ARJUN","Rs 999/mo subscription",
     [["IT-37","Demand validation"],["IT-38","Multi-portal scraper"],["IT-42","Beta 10 users"]]],
    ["QPF","QuickPay Finance","plan","low","India crypto exchange + FIAT gateway + DEX - future property",
     "#",JIRA+"/jira/software/projects/QPF/boards",3,0,0,"TARA (validation)","Long-term SaaS",
     [["QPF-1","India exchange"],["QPF-2","On/Off ramp"],["QPF-3","DEX"]]],
    ["SF","SendMoney Finance","plan","low","International money transfer + stablecoin INRT",
     "#",JIRA+"/jira/software/projects/SF/boards",7,0,0,"TARA (validation)","Long-term fintech",
     [["SF-1","Landing branding"],["SF-6","Stable coin INRT"],["SF-2","KYC dashboard"]]],
]

JS_LOGIC = r"""
const S={mailAcct:null,mailPage:1,mailUid:null};
let logs=[];let cdTimer=30;

function tab(name,el){
  document.querySelectorAll('.tp').forEach(function(t){t.classList.add('hidden');});
  document.querySelectorAll('.nav-tab').forEach(function(t){t.classList.remove('active');});
  document.getElementById('tp-'+name).classList.remove('hidden');
  if(el)el.classList.add('active');
  if(name==='mailbox')initMailbox();
  if(name==='sprint')loadSprint();
  if(name==='systems')loadSystems();
}

function tick(){var el=document.getElementById('clock');if(el)el.textContent=new Date().toLocaleTimeString('en-IN',{timeZone:'Asia/Calcutta',hour12:true});}
setInterval(tick,1000);tick();

function ring(pct,col){
  var r=22,c=2*Math.PI*r,off=c-(pct/100)*c;
  return '<svg class="ring-svg" width="52" height="52" viewBox="0 0 52 52"><circle class="ring-bg" cx="26" cy="26" r="'+r+'"/><circle class="ring-fg" cx="26" cy="26" r="'+r+'" stroke="'+col+'" stroke-dasharray="'+c+'" stroke-dashoffset="'+off+'"/></svg>';
}

function renderAgents(){
  var g=document.getElementById('agents-grid');
  if(!g)return;
  g.innerHTML='';
  AGENTS.forEach(function(a){
    var sc=a[2]==='live'?'b-live':a[2]==='build'?'b-build':'b-plan';
    var dc=a[2]==='live'?'dot-g pulse':a[2]==='build'?'dot-o pulse':'dot-b';
    var sl=a[2]==='live'?'LIVE':a[2]==='build'?'BUILDING':'PLANNED';
    var util=a[4];
    var rc=util>=70?'#4ade80':util>=40?'#fbbf24':'#818cf8';
    var uc=util>=70?'text-green-400':util>=40?'text-yellow-400':'text-indigo-400';
    var kpiHtml=a[6].map(function(k){return '<div class="text-center"><div class="text-slate-500" style="font-size:.65rem">'+k[1]+'</div><div class="text-white text-sm font-bold">'+k[0]+'</div></div>';}).join('');
    var jiraHtml=a[7].map(function(j){return '<a href="https://itgyani.atlassian.net/browse/'+j[0]+'" target="_blank" class="flex items-center gap-1 hover:text-indigo-300" style="text-decoration:none"><span class="text-indigo-500 font-mono shrink-0" style="font-size:.7rem">'+j[0]+'</span><span class="text-slate-400" style="font-size:.72rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:155px">'+j[1]+'</span></a>';}).join('');
    g.innerHTML+='<div class="card2 p-3 flex flex-col gap-2" style="border:1px solid transparent">'
      +'<div class="flex items-start justify-between">'
      +'<div class="flex items-center gap-2"><span class="dot '+dc+'" style="margin-top:3px"></span>'
      +'<div><div class="flex items-center gap-1.5" style="flex-wrap:wrap">'
      +'<span class="text-white font-bold" style="font-size:.85rem">'+a[0]+'</span>'
      +'<span class="badge '+sc+'">'+sl+'</span></div>'
      +'<div class="text-slate-500" style="font-size:.72rem">'+a[1]+'</div></div></div>'
      +'<div class="ring-wrap">'+ring(util,rc)+'<div class="ring-lbl '+uc+'">'+util+'%</div></div></div>'
      +'<div class="text-slate-400 leading-relaxed" style="font-size:.75rem;border-left:2px solid #334155;padding-left:8px">'+a[3]+'</div>'
      +'<div class="grid grid-cols-3 gap-1 rounded p-2" style="background:#0f172a40">'+kpiHtml+'</div>'
      +'<div><div class="text-slate-600 font-semibold uppercase" style="font-size:.6rem;letter-spacing:.08em;margin-bottom:4px">Jira Tickets</div>'
      +'<div class="space-y-0.5">'+jiraHtml+'</div></div>'
      +'<div class="flex items-center justify-between pt-1" style="border-top:1px solid #1f2d40">'
      +'<span class="text-slate-600" style="font-size:.7rem">Model: <span class="text-slate-400">'+a[5]+'</span></span>'
      +'<span class="'+uc+' font-semibold" style="font-size:.7rem">'+util+'% util</span></div></div>';
  });
}

function renderProjects(){
  var g=document.getElementById('projects-grid');
  if(!g)return;
  g.innerHTML='';
  PROJECTS.forEach(function(p){
    var pct=p[7]>0?Math.round(p[8]/p[7]*100):0;
    var sc=p[2]==='active'?'b-live':p[2]==='build'?'b-build':'b-plan';
    var sl=p[2]==='active'?'ACTIVE':p[2]==='build'?'BUILDING':'PLANNED';
    var pc=p[3]==='high'?'b-hi':p[3]==='med'?'b-med':'b-lo';
    var mHtml=p[11].map(function(m){return '<a href="https://itgyani.atlassian.net/browse/'+m[0]+'" target="_blank" class="flex items-center gap-1 hover:text-indigo-300" style="text-decoration:none;font-size:.72rem"><span class="text-indigo-500 font-mono shrink-0">'+m[0]+'</span><span class="text-slate-400" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+m[1]+'</span></a>';}).join('');
    var liveBtn=p[5]!=='#'?'<a href="'+p[5]+'" target="_blank" class="btn btn-g text-xs" style="flex:1;text-align:center">Live</a>':'';
    g.innerHTML+='<div class="proj-card flex flex-col gap-2">'
      +'<div><div class="flex items-center gap-1.5" style="flex-wrap:wrap;margin-bottom:3px">'
      +'<span class="text-white font-bold">'+p[1]+'</span>'
      +'<span class="badge '+sc+'">'+sl+'</span>'
      +'<span class="badge '+pc+'">'+p[3].toUpperCase()+'</span></div>'
      +'<div class="text-slate-500" style="font-size:.72rem">'+p[4]+'</div></div>'
      +'<div class="grid grid-cols-3 gap-2 text-center rounded p-2" style="background:#0f172a40">'
      +'<div><div class="text-green-400 font-bold text-lg">'+p[8]+'</div><div class="text-slate-600" style="font-size:.65rem">Done</div></div>'
      +'<div><div class="text-orange-400 font-bold text-lg">'+p[9]+'</div><div class="text-slate-600" style="font-size:.65rem">In Prog</div></div>'
      +'<div><div class="text-slate-300 font-bold text-lg">'+(p[7]-p[8]-p[9])+'</div><div class="text-slate-600" style="font-size:.65rem">To Do</div></div></div>'
      +'<div class="pb"><div class="pf pf-g" style="width:'+pct+'%"></div></div>'
      +'<div class="flex items-center justify-between text-slate-500" style="font-size:.72rem">'
      +'<span>'+pct+'% - '+p[7]+' issues</span><span>'+p[10]+'</span></div>'
      +'<div class="text-slate-500" style="font-size:.72rem">'+p[11+0-11+10]+'... '+p[12]+'</div>'
      +'<div style="font-size:.72rem;color:#6b7280">'+p[12]+'</div>'
      +'<div class="space-y-0.5 pt-1" style="border-top:1px solid #1f2d40">'
      +'<div class="text-slate-600 font-semibold uppercase" style="font-size:.6rem;letter-spacing:.08em;margin-bottom:4px">Next Milestones</div>'
      +mHtml+'</div>'
      +'<div class="flex gap-1 pt-1">'+liveBtn
      +'<a href="'+p[6]+'" target="_blank" class="btn btn-g text-xs" style="flex:1;text-align:center">Jira Board</a></div></div>';
  });
}

async function initMailbox(){
  try{
    var r=await fetch('/api/accounts');
    if(r.status===401||r.status===403){showMailLogin();return;}
    var accounts=await r.json();
    if(!Array.isArray(accounts)){showMailLogin();return;}
    renderAccounts(accounts);
    if(accounts.length>0&&!S.mailAcct)selectAccount(accounts[0].email,accounts[0].label);
  }catch(e){showMailLogin();}
}
function showMailLogin(){
  document.getElementById('acct-list').innerHTML='<div style="color:#6b7280;font-size:.78rem;padding:8px">Login required</div>';
  document.getElementById('email-list').innerHTML='';
  document.getElementById('reader-empty').classList.add('hidden');
  document.getElementById('reader-content').classList.add('hidden');
  document.getElementById('mail-login-prompt').classList.remove('hidden');
}
async function mailLogin(){
  var fd=new FormData();
  fd.append('username',document.getElementById('ml-user').value);
  fd.append('password',document.getElementById('ml-pass').value);
  document.getElementById('ml-err').classList.add('hidden');
  try{
    await fetch('/login',{method:'POST',body:fd,redirect:'follow'});
    var r=await fetch('/api/accounts');
    if(r.ok){
      document.getElementById('mail-login-prompt').classList.add('hidden');
      var a=await r.json();renderAccounts(a);
      if(a.length>0)selectAccount(a[0].email,a[0].label);
      addLog('Mailbox unlocked','g');
    }else{document.getElementById('ml-err').classList.remove('hidden');}
  }catch(e){document.getElementById('ml-err').classList.remove('hidden');}
}
function renderAccounts(accounts){
  var el=document.getElementById('acct-list');el.innerHTML='';
  accounts.forEach(function(a){
    var u=a.unread||0;
    el.innerHTML+='<div class="acc-item flex items-center justify-between" data-email="'+a.email+'" onclick="selectAccount(\''+a.email+'\',\''+(a.label||a.email)+'\')">'
      +'<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+(a.label||a.email.split('@')[0])+'</span>'
      +(u>0?'<span style="font-size:.7rem;background:#312e81;color:#a5b4fc;padding:1px 6px;border-radius:8px;flex-shrink:0">'+(u>99?'99+':u)+'</span>':'')+'</div>';
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
  var el=document.getElementById('email-list');
  el.innerHTML='<div style="color:#6b7280;font-size:.78rem;padding:16px;text-align:center"><span class="spin"></span></div>';
  try{
    var r=await fetch('/api/emails?account='+encodeURIComponent(S.mailAcct)+'&page='+S.mailPage+'&limit=20');
    if(r.status===401){showMailLogin();return;}
    var d=await r.json();var emails=d.emails||[];
    el.innerHTML='';
    if(!emails.length){el.innerHTML='<div style="color:#6b7280;font-size:.78rem;padding:16px;text-align:center">No emails</div>';return;}
    emails.forEach(function(e){
      var from=(e.from_addr||'').replace(/<[^>]+>/g,'').trim().split('@')[0].substring(0,18);
      var subj=(e.subject||'(no subject)').substring(0,40);
      var date=e.date_str?e.date_str.substring(0,10):'';
      el.innerHTML+='<div class="email-row'+((!e.is_read)?' unread':'')+'" onclick="openEmail(\''+( e.uid||e.id)+'\')">'
        +'<div class="flex items-center justify-between" style="margin-bottom:2px">'
        +'<span style="color:#cbd5e1;font-size:.75rem;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+from+'</span>'
        +'<span style="color:#4b5563;font-size:.7rem;flex-shrink:0">'+date+'</span></div>'
        +'<div class="e-subj" style="color:#6b7280;font-size:.75rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+subj+'</div></div>';
    });
  }catch(e){el.innerHTML='<div style="color:#f87171;font-size:.78rem;padding:12px">Error: '+e.message+'</div>';}
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
    var r=await fetch('/api/emails/'+encodeURIComponent(S.mailAcct)+'/'+uid);
    var d=await r.json();var e=d.email||d;
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
  var txt=document.getElementById('reply-txt').value.trim();
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
async function syncEmail(){try{await fetch('/api/sync/quick',{method:'POST'});addLog('Email sync triggered','b');setTimeout(function(){if(S.mailAcct)loadEmails();},3000);}catch(e){}}

function getTasks(){try{return JSON.parse(localStorage.getItem('ig_tasks')||'[]');}catch(e){return [];}}
function saveTasks(t){localStorage.setItem('ig_tasks',JSON.stringify(t));}
function addTask(){
  var title=document.getElementById('t-title').value.trim();if(!title)return;
  var tasks=getTasks();
  tasks.unshift({id:Date.now(),title:title,agent:document.getElementById('t-agent').value,prio:document.getElementById('t-prio').value,status:'todo',created:new Date().toISOString()});
  saveTasks(tasks);document.getElementById('t-title').value='';renderTasks();
  addLog('Task dispatched to '+document.getElementById('t-agent').value+': '+title,'b');
}
function cycleTask(id){var tasks=getTasks();var t=tasks.find(function(x){return x.id===id;});if(!t)return;var seq=['todo','doing','done'];t.status=seq[(seq.indexOf(t.status)+1)%seq.length];saveTasks(tasks);renderTasks();}
function delTask(id){saveTasks(getTasks().filter(function(x){return x.id!==id;}));renderTasks();}
function renderTasks(){
  var tasks=getTasks();var cols={todo:[],doing:[],done:[]};
  tasks.forEach(function(t){if(cols[t.status])cols[t.status].push(t);});
  ['todo','doing','done'].forEach(function(st){
    var col=document.getElementById('col-'+st);var cnt=document.getElementById('cnt-'+st);
    if(cnt)cnt.textContent=cols[st].length;if(!col)return;
    if(!cols[st].length){col.innerHTML='<div style="color:#374151;font-size:.75rem;text-align:center;padding:16px">Empty</div>';return;}
    col.innerHTML=cols[st].map(function(t){
      var pc=t.prio==='high'?'b-hi':t.prio==='med'?'b-med':'b-lo';
      return '<div class="task-card'+(st==='done'?' done-card':'')+'" onclick="cycleTask('+t.id+')">'
        +'<div class="flex items-start justify-between gap-1" style="margin-bottom:4px">'
        +'<span style="color:#e2e8f0;font-size:.85rem;font-weight:500">'+t.title+'</span>'
        +'<button style="color:#4b5563;cursor:pointer;border:none;background:none;flex-shrink:0" onclick="event.stopPropagation();delTask('+t.id+')">x</button></div>'
        +'<div class="flex items-center gap-1.5"><span style="color:#818cf8;font-size:.72rem">'+t.agent+'</span><span class="badge '+pc+'">'+t.prio+'</span></div></div>';
    }).join('');
  });
}

async function loadSprint(){
  try{
    var r=await fetch('/api/ops/jira-sprint',{cache:'no-store'});
    if(!r.ok)throw new Error('HTTP '+r.status);
    var d=await r.json();
    var done=d.done||0,total=d.total||0,inp=d.in_progress||0;
    document.getElementById('k-j').textContent=done+'/'+total;
    document.getElementById('k-j-l').textContent='Done of '+total+' issues';
    document.getElementById('k-j-b').style.width=(total>0?(done/total*100):0)+'%';
    document.getElementById('sprint-meta').textContent=total+' issues - '+done+' done - '+inp+' in progress - '+(total-done-inp)+' to do';
    var jt=document.getElementById('j-todo'),jp=document.getElementById('j-prog'),jd=document.getElementById('j-done');
    jt.innerHTML='';jp.innerHTML='';jd.innerHTML='';
    (d.issues||[]).forEach(function(i){
      var cat=i.status_cat||'new';
      var card='<div class="card2 p-2" style="margin-bottom:6px;font-size:.78rem">'
        +'<a href="https://itgyani.atlassian.net/browse/'+i.key+'" target="_blank" style="color:#818cf8;font-weight:700">'+i.key+'</a>'
        +'<div style="color:#cbd5e1;margin-top:3px;line-height:1.4">'+i.summary+'</div>'
        +(i.assignee&&i.assignee!=='Unassigned'?'<div style="color:#4b5563;margin-top:2px">'+i.assignee+'</div>':'')+'</div>';
      if(cat==='done')jd.innerHTML+=card;
      else if(cat==='indeterminate')jp.innerHTML+=card;
      else jt.innerHTML+=card;
    });
    if(!jt.innerHTML)jt.innerHTML='<div style="color:#374151;font-size:.75rem;padding:8px;text-align:center">Empty</div>';
    if(!jp.innerHTML)jp.innerHTML='<div style="color:#374151;font-size:.75rem;padding:8px;text-align:center">Empty</div>';
    if(!jd.innerHTML)jd.innerHTML='<div style="color:#374151;font-size:.75rem;padding:8px;text-align:center">Empty</div>';
  }catch(e){
    ['j-todo','j-prog','j-done'].forEach(function(id){var el=document.getElementById(id);if(el)el.innerHTML='<div style="color:#fbbf24;font-size:.75rem;padding:8px">Jira: '+e.message+'</div>';});
  }
}

async function loadSystems(){
  try{
    var r=await fetch('/api/ops/status',{cache:'no-store'});
    if(!r.ok)throw new Error('HTTP '+r.status);
    var d=await r.json();
    var sr=d.strategies||{};
    document.getElementById('k-s').textContent=(sr.running||10)+'/'+(sr.configured||10);
    document.getElementById('k-s-b').style.width=(sr.configured>0?(sr.running/sr.configured*100):100)+'%';
    document.getElementById('k-c').textContent=(d.chartink&&d.chartink.total)||15;
    var cc=document.getElementById('sys-c');cc.innerHTML='';
    (d.containers||[]).forEach(function(c){
      cc.innerHTML+='<div class="flex items-center justify-between p-2 card2 rounded" style="margin-bottom:4px">'
        +'<div><div style="color:#e2e8f0;font-size:.85rem">'+c.name+'</div>'
        +'<div style="color:#6b7280;font-size:.72rem">'+c.status.substring(0,35)+'</div></div>'
        +'<div class="flex items-center gap-1"><div class="dot '+(c.ok?'dot-g pulse':'dot-r')+'"></div>'
        +'<span style="font-size:.75rem;color:'+(c.ok?'#4ade80':'#f87171')+'">'+(c.ok?'Up':'Down')+'</span></div></div>';
    });
    document.getElementById('sync-lbl').textContent='Synced '+new Date(d.timestamp||Date.now()).toLocaleTimeString('en-IN',{timeZone:'Asia/Calcutta',hour12:true});
    addLog('Systems synced: '+(d.containers||[]).length+' containers','g');
  }catch(e){
    document.getElementById('sync-lbl').textContent='API offline';
    document.getElementById('k-s').textContent='10/10';
    document.getElementById('k-c').textContent='15';
    addLog('Status API: '+e.message,'r');
  }
}

function addLog(msg,type){
  type=type||'b';
  var now=new Date().toLocaleTimeString('en-IN',{timeZone:'Asia/Calcutta',hour12:true});
  logs.unshift({msg:msg,type:type,time:now});if(logs.length>60)logs.pop();renderLogs();
}
function renderLogs(){
  var el=document.getElementById('live-log');if(!el)return;
  if(!logs.length){el.innerHTML='<div style="color:#374151;font-size:.85rem;text-align:center;padding:32px">No activity yet</div>';return;}
  var color={g:'#166534',o:'#9a3412',r:'#991b1b',b:'#3730a3'};
  el.innerHTML=logs.slice(0,50).map(function(l){return '<div style="padding:7px 10px;border-left:2px solid '+(color[l.type]||color.b)+';margin-bottom:5px;font-size:.78rem"><span style="color:#4b5