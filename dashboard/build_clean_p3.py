#!/usr/bin/env python3
"""Part 3 - final JS and close HTML"""
import os

OUT = '/opt/itgyani-dashboard/frontend/ops.html'

PART3 = '''return JSON.parse(localStorage.getItem('ig_tasks')||'[]');} catch(e){return [];}}
function saveTasks(t) { localStorage.setItem('ig_tasks', JSON.stringify(t)); }
function addTask() {
  var ti = document.getElementById('t-title').value.trim();
  if (!ti) return;
  var tasks = getTasks();
  var agent = document.getElementById('t-agent').value;
  var prio = document.getElementById('t-prio').value;
  tasks.unshift({id:Date.now(), title:ti, agent:agent, prio:prio, status:'todo', created:new Date().toISOString()});
  saveTasks(tasks);
  document.getElementById('t-title').value = '';
  renderTasks();
  addLog('Task → '+agent+': '+ti, 'b');
}
function cycleTask(id) {
  var tasks = getTasks();
  var t = tasks.find(function(x){return x.id===id;});
  if (!t) return;
  var seq = ['todo','doing','done'];
  t.status = seq[(seq.indexOf(t.status)+1)%seq.length];
  saveTasks(tasks); renderTasks();
}
function delTask(id) { saveTasks(getTasks().filter(function(x){return x.id!==id;})); renderTasks(); }
function renderTasks() {
  var tasks = getTasks();
  var cols = {todo:[], doing:[], done:[]};
  tasks.forEach(function(t){if(cols[t.status])cols[t.status].push(t);});
  [['todo','cnt-todo','col-todo'],['doing','cnt-doing','col-doing'],['done','cnt-done','col-done']].forEach(function(x){
    var cnt = document.getElementById(x[0]); if(cnt) cnt.textContent=cols[x[0]].length;
    var col = document.getElementById(x[2]); if(!col) return;
    if(!cols[x[0]].length){col.innerHTML='<div style="color:#374151;font-size:.75rem;text-align:center;padding:16px">Empty</div>';return;}
    var prioStyles = {high:'background:#450a0a;color:#f87171;border:1px solid #991b1b',med:'background:#1c1917;color:#fbbf24;border:1px solid #92400e',low:'background:#111827;color:#6b7280;border:1px solid #374151'};
    col.innerHTML = cols[x[0]].map(function(t){
      var ps = prioStyles[t.prio] || prioStyles.low;
      return '<div class="tc'+(x[0]==='done'?' dnc':'')+'" onclick="cycleTask('+t.id+')">'
        +'<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:4px;margin-bottom:4px">'
        +'<span style="color:#e2e8f0;font-size:.85rem;font-weight:500">'+t.title+'</span>'
        +'<button style="color:#4b5563;cursor:pointer;border:none;background:none;flex-shrink:0;font-size:1rem;line-height:1" onclick="event.stopPropagation();delTask('+t.id+')">&#x2715;</button></div>'
        +'<div style="display:flex;align-items:center;gap:6px"><span style="color:#818cf8;font-size:.72rem">'+t.agent+'</span>'
        +'<span style="display:inline-flex;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px;'+ps+'">'+t.prio+'</span></div></div>';
    }).join('');
  });
}

// ========== MOM ==========
async function saveMOM() {
  var ti = document.getElementById('mom-t').value.trim();
  var no = document.getElementById('mom-n').value.trim();
  if (!ti) return;
  var date = new Date().toLocaleDateString('en-IN');
  try {
    await fetch('/api/ops/mom', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({title:ti, notes:no, date:date})});
  } catch(e){}
  document.getElementById('mom-t').value='';
  document.getElementById('mom-n').value='';
  document.getElementById('mom-frm').classList.add('hidden');
  loadMOM();
  addLog('MOM saved: '+ti, 'b');
}
async function loadMOM() {
  try {
    var r = await fetch('/api/ops/mom');
    var entries = await r.json();
    var el = document.getElementById('mom-list');
    if (!entries.length){el.innerHTML='<div style="color:#374151;text-align:center;padding:24px">No meetings yet.</div>';return;}
    el.innerHTML = entries.slice(-8).reverse().map(function(m){
      return '<div style="padding:8px 10px;border-left:2px solid #3730a3;margin-bottom:6px">'
        +'<div style="display:flex;justify-content:space-between;margin-bottom:4px">'
        +'<span style="color:#e2e8f0;font-weight:600;font-size:.8rem">'+m.title+'</span>'
        +'<span style="color:#4b5563;font-size:.75rem">'+m.date+'</span></div>'
        +'<div style="color:#94a3b8;font-size:.78rem;white-space:pre-wrap">'+(m.notes||'')+'</div></div>';
    }).join('');
  } catch(e){}
}

// ========== LOAD ALL ==========
async function loadAll() {
  addLog('Refreshing dashboard...','b');
  await Promise.all([loadSys(), loadSprint(), loadMOM()]);
  countdown = 15;
}

// ========== INIT ==========
renderTasks();
loadAll();
setTimeout(function(){
  addLog('ITGYANI OS v3 online','g');
  addLog('14 agents: 10 LIVE / 2 BUILDING / 2 PLANNED','g');
  addLog('8 projects | Jira boards linked | 15-min refresh','b');
}, 800);
</script>
</body>
</html>'''

with open(OUT, 'a') as f:
    f.write(PART3)

size = os.path.getsize(OUT)
print(f'Done. Total size: {size} bytes')

# Verify integrity
content = open(OUT).read()
checks = {
    'Single tab function': content.count('function switchTab') == 1,
    'No old tab() fn': content.count('function tab(') == 0,
    'Single </html>': content.count('</html>') == 1,
    'Agent cards': 'RONY' in content and 'KABIR' in content and 'RAVI' in content,
    'Project cards': 'CryptoGyani' in content and 'YUKTI' in content,
    '15 min refresh': '15' in content and 'countdown' in content,
    'Jira links': 'itgyani.atlassian.net/browse/IT-34' in content,
}
for k,v in checks.items():
    print(f'{"OK" if v else "FAIL"}: {k}')
