#!/usr/bin/env python3
"""Part 3: finish and close ops.html"""
import os

OUT = '/opt/itgyani-dashboard/frontend/ops.html'

TAIL = r"""563">'+l.time+'</span><span style="color:#cbd5e1;margin-left:8px">'+l.msg+'</span></div>';}).join('');
}

async function saveMOM(){
  var title=document.getElementById('mom-t').value.trim();
  var notes=document.getElementById('mom-n').value.trim();
  if(!title)return;
  var date=new Date().toLocaleDateString('en-IN');
  try{await fetch('/api/ops/mom',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:title,notes:notes,date:date})});}catch(e){}
  document.getElementById('mom-t').value='';document.getElementById('mom-n').value='';
  document.getElementById('mom-frm').classList.add('hidden');
  loadMOM();addLog('MOM saved: '+title,'b');
}
async function loadMOM(){
  try{
    var r=await fetch('/api/ops/mom');var entries=await r.json();
    var el=document.getElementById('mom-list');
    if(!entries.length){el.innerHTML='<div style="color:#374151;font-size:.85rem;text-align:center;padding:24px">No meetings yet.</div>';return;}
    el.innerHTML=entries.slice(-8).reverse().map(function(m){return '<div style="padding:8px 10px;border-left:2px solid #3730a3;margin-bottom:6px"><div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="color:#e2e8f0;font-weight:600;font-size:.8rem">'+m.title+'</span><span style="color:#4b5563;font-size:.75rem">'+m.date+'</span></div><div style="color:#94a3b8;font-size:.78rem;white-space:pre-wrap">'+( m.notes||'')+'</div></div>';}).join('');
  }catch(e){}
}

async function loadAll(){
  addLog('Refreshing all data...','b');
  await Promise.all([loadSystems(),loadSprint(),loadMOM()]);
  cdTimer=30;
}

setInterval(function(){
  cdTimer--;
  var el=document.getElementById('cd');if(el)el.textContent=cdTimer>0?cdTimer:'...';
  if(cdTimer<=0){cdTimer=30;loadAll();}
},1000);

renderAgents();
renderProjects();
renderTasks();
loadAll();
setTimeout(function(){
  addLog('ITGYANI OS v3 Command Center online','g');
  addLog('14 agents: 10 LIVE / 2 BUILDING / 2 PLANNED','g');
  addLog('8 projects | 135 Jira issues | All boards linked','b');
},700);
</script>
</body>
</html>
"""

with open(OUT, 'a') as f:
    f.write(TAIL)

size = os.path.getsize(OUT)
print(f'ops.html final size: {size} bytes')
