content = r"""
-content').classList.add('hidden');
    loadEmails();addLog('Deleted email','o');
  }catch(e){alert('Delete failed: '+e.message);}
}
function mailPage(d){S.mailPage=Math.max(1,S.mailPage+d);loadEmails();}
async function syncEmail(){
  try{await fetch('/api/sync/quick',{method:'POST'});addLog('Email sync triggered','b');setTimeout(()=>{if(S.mailAcct)loadEmails();},3000);}catch{}
}

// ── TASKS ──────────────────────────────────────────────────────────────────────
function getTasks(){try{return JSON.parse(localStorage.getItem('ig_tasks')||'[]');}catch{return [];}}
function saveTasks(t){localStorage.setItem('ig_tasks',JSON.stringify(t));}
function addTask(){
  const title=document.getElementById('t-title').value.trim();
  if(!title)return;
  const tasks=getTasks();
  tasks.unshift({id:Date.now(),title,agent:document.getElementById('t-agent').value,prio:document.getElementById('t-prio').value,status:'todo',created:new Date().toISOString()});
  saveTasks(tasks);document.getElementById('t-title').value='';renderTasks();
  addLog(`Task dispatched to ${document.getElementById('t-agent').value}: "${title}"`,'b');
}
function cycleTask(id){const tasks=getTasks();const t=tasks.find(x=>x.id===id);if(!t)return;const seq=['todo','doing','done'];t.status=seq[(seq.indexOf(t.status)+1)%seq.length];saveTasks(tasks);renderTasks();}
function delTask(id){saveTasks(getTasks().filter(x=>x.id!==id));renderTasks();}
function renderTasks(){
  const tasks=getTasks();
  const cols={todo:[],doing:[],done:[]};
  tasks.forEach(t=>{if(cols[t.status])cols[t.status].push(t);});
  ['todo','doing','done'].forEach(st=>{
    const col=document.getElementById('col-'+st);
    const cnt=document.getElementById('cnt-'+st);
    if(cnt)cnt.textContent=cols[st].length;
    if(!col)return;
    if(!cols[st].length){col.innerHTML='<div class="text-slate-700 text-xs text-center py-4">Empty</div>';return;}
    col.innerHTML=cols[st].map(t=>{
      const pc=t.prio==='high'?'b-hi':t.prio==='med'?'b-med':'b-lo';
      return `<div class="task-card ${st==='done'?'done-card':''}" onclick="cycleTask(${t.id})">
        <div class="flex items-start justify-between gap-1 mb-1">
          <span class="text-slate-200 text-sm font-medium">${t.title}</span>
          <button class="text-slate-600 hover:text-red-400 shrink-0" onclick="event.stopPropagation();delTask(${t.id})">×</button>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="text-indigo-400 text-xs">${t.agent}</span>
          <span class="badge ${pc}">${t.prio}</span>
        </div>
      </div>`;
    }).join('');
  });
}

// ── SPRINT ─────────────────────────────────────────────────────────────────────
async function loadSprint(){
  try{
    const r=await fetch('/api/ops/jira-sprint',{cache:'no-store'});
    if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();
    const done=d.done||0,total=d.total||0,inp=d.in_progress||0;
    document.getElementById('k-j').textContent=`${done}/${total}`;
    document.getElementById('k-j-l').textContent=`Done of ${total} stories`;
    document.getElementById('k-j-b').style.width=total>0?(done/total*100)+'%':'0%';
    document.getElementById('sprint-meta').textContent=`${total} issues · ${done} done · ${inp} in progress · ${total-done-inp} to do`;
    const jt=document.getElementById('j-todo'),jp=document.getElementById('j-prog'),jd=document.getElementById('j-done');
    jt.innerHTML='';jp.innerHTML='';jd.innerHTML='';
    (d.issues||[]).forEach(i=>{
      const cat=i.status_cat||'new';
      const card=`<div class="card2 p-2 mb-1.5 text-xs">
        <a href="https://itgyani.atlassian.net/browse/${i.key}" target="_blank" class="text-indigo-400 font-semibold hover:text-indigo-300">${i.key}</a>
        <div class="text-slate-300 mt-0.5 leading-snug">${i.summary}</div>
        ${i.assignee&&i.assignee!=='Unassigned'?`<div class="text-slate-600 mt-0.5">${i.assignee}</div>`:''}
      </div>`;
      if(cat==='done')jd.innerHTML+=card;
      else if(cat==='indeterminate')jp.innerHTML+=card;
      else jt.innerHTML+=card;
    });
    if(!jt.innerHTML)jt.innerHTML='<div class="text-slate-700 text-xs py-2 text-center">Empty</div>';
    if(!jp.innerHTML)jp.innerHTML='<div class="text-slate-700 text-xs py-2 text-center">Empty</div>';
    if(!jd.innerHTML)jd.innerHTML='<div class="text-slate-700 text-xs py-2 text-center">Empty</div>';
  }catch(e){
    ['j-todo','j-prog','j-done'].forEach(id=>{const el=document.getElementById(id);if(el)el.innerHTML=`<div class="text-yellow-500 text-xs py-2">Jira: ${e.message}</div>`;});
  }
}

// ── SYSTEMS ────────────────────────────────────────────────────────────────────
async function loadSystems(){
  try{
    const r=await fetch('/api/ops/status',{cache:'no-store'});
    if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();
    const sr=d.strategies||{};
    document.getElementById('k-s').textContent=`${sr.running||10}/${sr.configured||10}`;
    document.getElementById('k-s-b').style.width=sr.configured>0?(sr.running/sr.configured*100)+'%':'100%';
    document.getElementById('k-c').textContent=d.chartink?.total||15;
    const cc=document.getElementById('sys-c');
    cc.innerHTML='';
    (d.containers||[]).forEach(c=>{
      cc.innerHTML+=`<div class="flex items-center justify-between p-2 card2 rounded">
        <div><div class="text-slate-200 text-sm">${c.name}</div><div class="text-slate-500 text-xs">${c.status.substring(0,35)}</div></div>
        <div class="flex items-center gap-1"><div class="dot ${c.ok?'dot-g pulse':'dot-r'}"></div><span class="text-xs ${c.ok?'text-green-400':'text-red-400'}">${c.ok?'Up':'Down'}</span></div>
      </div>`;
    });
    document.getElementById('sync-lbl').textContent='Synced '+new Date(d.timestamp||Date.now()).toLocaleTimeString('en-IN',{timeZone:'Asia/Calcutta',hour12:true});
    addLog(`Systems synced: ${(d.containers||[]).length} containers`,'g');
  }catch(e){
    document.getElementById('sync-lbl').textContent='API offline';
    document.getElementById('k-s').textContent='10/10';
    document.getElementById('k-c').textContent='15';
    addLog('Status API: '+e.message,'r');
  }
}

// ── LOGS ───────────────────────────────────────────────────────────────────────
function addLog(msg,type='b'){
  const now=new Date().toLocaleTimeString('en-IN',{timeZone:'Asia/Calcutta',hour12:true});
  logs.unshift({msg,type,time:now});if(logs.length>80)logs.pop();renderLogs();
}
function renderLogs(){
  const el=document.getElementById('live-log');
  if(!logs.length){el.innerHTML='<div class="text-slate-600 text-sm text-center py-8">No activity yet</div>';return;}
  const color={g:'#166534',o:'#9a3412',r:'#991b1b',b:'#3730a3'};
  el.innerHTML=logs.slice(0,50).map(l=>`<div style="padding:7px 10px;border-left:2px solid ${color[l.type]||color.b};margin-bottom:5px;font-size:.78rem"><span style="color:#4b5563">${l.time}</span><span style="color:#cbd5e1;margin-left:8px">${l.msg}</span></div>`).join('');
}

// ── MOM ────────────────────────────────────────────────────────────────────────
async function saveMOM(){
  const title=document.getElementById('mom-t').value.trim();
  const notes=document.getElementById('mom-n').value.trim();
  if(!title)return;
  const date=new Date().toLocaleDateString('en-IN');
  try{await fetch('/api/ops/mom',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title,notes,date})});}catch{}
  document.getElementById('mom-t').value='';document.getElementById('mom-n').value='';
  document.getElementById('mom-frm').classList.add('hidden');
  loadMOM();addLog('MOM saved: '+title,'b');
}
async function loadMOM(){
  try{
    const r=await fetch('/api/ops/mom');const entries=await r.json();
    const el=document.getElementById('mom-list');
    if(!entries.length){el.innerHTML='<div class="text-slate-600 text-sm text-center py-6">No meetings yet.</div>';return;}
    el.innerHTML=entries.slice(-8).reverse().map(m=>`<div style="padding:8px 10px;border-left:2px solid #3730a3;margin-bottom:6px">
      <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="color:#e2e8f0;font-weight:600;font-size:.8rem">${m.title}</span><span style="color:#4b5563;font-size:.75rem">${m.date}</span></div>
      <div style="color:#94a3b8;font-size:.78rem;white-space:pre-wrap">${m.notes||''}</div>
    </div>`).join('');
  }catch{}
}

// ── LOAD ALL ───────────────────────────────────────────────────────────────────
async function loadAll(){
  addLog('Refreshing all data…','b');
  await Promise.all([loadSystems(),loadSprint(),loadMOM()]);
  cdTimer=30;
}

// ── AUTO REFRESH ───────────────────────────────────────────────────────────────
setInterval(()=>{
  cdTimer--;
  const el=document.getElementById('cd');if(el)el.textContent=cdTimer>0?cdTimer:'…';
  if(cdTimer<=0){cdTimer=30;loadAll();}
},1000);

// ── BOOT ───────────────────────────────────────────────────────────────────────
renderAgents();
renderProjects();
renderTasks();
loadAll();
setTimeout(()=>{
  addLog('ITGYANI OS v3 Command Center online','g');
  addLog('14 agents: 10 LIVE / 2 BUILDING / 2 PLANNED','g');
  addLog('8 projects tracked | Jira links wired to all tickets','b');
},600);
</script>
</body>
</html>
"""

with open(r'C:\Antigravity\projects\open-claw-rony\dashboard\frontend\ops.html', 'a', encoding='utf-8') as f:
    f.write(content)

import os
size = os.path.getsize(r'C:\Antigravity\projects\open-claw-rony\dashboard\frontend\ops.html')
print(f"Total size: {size} bytes")
