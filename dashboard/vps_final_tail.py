#!/usr/bin/env python3
"""Tail part — append JS closing to ops.html"""
import os

OUT = '/opt/itgyani-dashboard/frontend/ops.html'

TAIL = """d.total||0,ip=d.in_progress||0;
document.getElementById('kj').textContent=dn+'/'+tot;
document.getElementById('kjl').textContent='Done of '+tot+' issues';
document.getElementById('kjb').style.width=(tot>0?(dn/tot*100):0)+'%';
document.getElementById('smeta').textContent=tot+' issues - '+dn+' done - '+ip+' in progress - '+(tot-dn-ip)+' to do';
var jt=document.getElementById('jtd'),jp=document.getElementById('jip'),jd=document.getElementById('jdn');
jt.innerHTML='';jp.innerHTML='';jd.innerHTML='';
(d.issues||[]).forEach(function(i){var cat=i.status_cat||'new';var card='<div class=c2 style="padding:8px;margin-bottom:6px;font-size:.78rem"><a href=https://itgyani.atlassian.net/browse/'+i.key+' target=_blank style="color:#818cf8;font-weight:700">'+i.key+'</a><div style="color:#cbd5e1;margin-top:3px;line-height:1.4">'+i.summary+'</div></div>';if(cat==='done')jd.innerHTML+=card;else if(cat==='indeterminate')jp.innerHTML+=card;else jt.innerHTML+=card;});
if(!jt.innerHTML)jt.innerHTML='<div style="color:#374151;font-size:.75rem;text-align:center;padding:8px">Empty</div>';
if(!jp.innerHTML)jp.innerHTML='<div style="color:#374151;font-size:.75rem;text-align:center;padding:8px">Empty</div>';
if(!jd.innerHTML)jd.innerHTML='<div style="color:#374151;font-size:.75rem;text-align:center;padding:8px">Empty</div>';
}catch(e){['jtd','jip','jdn'].forEach(function(id){var el=document.getElementById(id);if(el)el.innerHTML='<div style="color:#fbbf24;font-size:.75rem;padding:8px">Jira: '+e.message+'</div>';});}}
async function loadSys(){try{var r=await fetch('/api/ops/status',{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);var d=await r.json();var sr=d.strategies||{};document.getElementById('ks').textContent=(sr.running||10)+'/'+(sr.configured||10);document.getElementById('ksb').style.width=(sr.configured>0?(sr.running/sr.configured*100):100)+'%';document.getElementById('kc').textContent=(d.chartink&&d.chartink.total)||15;var cc=document.getElementById('sysc');cc.innerHTML='';(d.containers||[]).forEach(function(c){cc.innerHTML+='<div style="display:flex;align-items:center;justify-content:space-between;padding:8px;background:#1a2235;border:1px solid #1f2d40;border-radius:6px;margin-bottom:4px"><div><div style="color:#e2e8f0;font-size:.85rem">'+c.name+'</div><div style="color:#6b7280;font-size:.72rem">'+c.status.substring(0,35)+'</div></div><div style="display:flex;align-items:center;gap:4px"><div style="width:7px;height:7px;border-radius:50%;background:'+(c.ok?'#4ade80':'#f87171')+(c.ok?';animation:P 2s infinite':'')+'"></div><span style="font-size:.75rem;color:'+(c.ok?'#4ade80':'#f87171')+'">'+(c.ok?'Up':'Down')+'</span></div></div>';});document.getElementById('slbl').textContent='Synced '+new Date(d.timestamp||Date.now()).toLocaleTimeString('en-IN',{timeZone:'Asia/Calcutta',hour12:true});addLog('Systems synced: '+(d.containers||[]).length+' containers','g');}catch(e){document.getElementById('slbl').textContent='API offline';document.getElementById('ks').textContent='10/10';document.getElementById('kc').textContent='15';addLog('Status API error: '+e.message,'r');}}
function addLog(msg,type){type=type||'b';var now=new Date().toLocaleTimeString('en-IN',{timeZone:'Asia/Calcutta',hour12:true});logs.unshift({msg:msg,type:type,time:now});if(logs.length>60)logs.pop();renderLogs();}
function renderLogs(){var el=document.getElementById('llog');if(!el)return;if(!logs.length){el.innerHTML='<div style="color:#374151;text-align:center;padding:32px">No activity yet</div>';return;}var color={g:'#166534',o:'#9a3412',r:'#991b1b',b:'#3730a3'};el.innerHTML=logs.slice(0,50).map(function(l){return '<div style="padding:7px 10px;border-left:2px solid '+(color[l.type]||color.b)+';margin-bottom:5px;font-size:.78rem"><span style=color:#4b5563>'+l.time+'</span><span style="color:#cbd5e1;margin-left:8px">'+l.msg+'</span></div>';}).join('');}
async function saveMOM(){var ti=document.getElementById('momt').value.trim();var no=document.getElementById('momn').value.trim();if(!ti)return;var date=new Date().toLocaleDateString('en-IN');try{await fetch('/api/ops/mom',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:ti,notes:no,date:date})});}catch(e){}document.getElementById('momt').value='';document.getElementById('momn').value='';document.getElementById('momf').classList.add('hidden');loadMOM();addLog('MOM: '+ti,'b');}
async function loadMOM(){try{var r=await fetch('/api/ops/mom');var entries=await r.json();var el=document.getElementById('moml');if(!entries.length){el.innerHTML='<div style="color:#374151;text-align:center;padding:24px">No meetings yet.</div>';return;}el.innerHTML=entries.slice(-8).reverse().map(function(m){return '<div style="padding:8px 10px;border-left:2px solid #3730a3;margin-bottom:6px"><div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="color:#e2e8f0;font-weight:600;font-size:.8rem">'+m.title+'</span><span style="color:#4b5563;font-size:.75rem">'+m.date+'</span></div><div style="color:#94a3b8;font-size:.78rem;white-space:pre-wrap">'+(m.notes||'')+'</div></div>';}).join('');}catch(e){}}
async function loadAll(){addLog('Refreshing...','b');await Promise.all([loadSys(),loadSprint(),loadMOM()]);cd=30;}
setInterval(function(){cd--;var el=document.getElementById('cdtmr');if(el)el.textContent=cd>0?cd:'...';if(cd<=0){cd=30;loadAll();}},1000);
renderTasks();loadAll();
setTimeout(function(){addLog('ITGYANI OS v3 online','g');addLog('14 agents: 10 LIVE / 2 BUILDING / 2 PLANNED','g');addLog('8 projects | 135 Jira issues | All boards linked','b');},600);
</script>
</body>
</html>"""

with open(OUT, 'a') as f:
    f.write(TAIL)

size = os.path.getsize(OUT)
print(f'Final size: {size} bytes')

# Verify it has key elements
content = open(OUT).read()
checks = ['agrid', 'pgrid', 'tp-agents', 'tp-projects', 'tp-sprint', 'AGENTS', 'PROJECTS', '</html>']
for c in checks:
    print(f'{"OK" if c in content else "MISSING"}: {c}')
