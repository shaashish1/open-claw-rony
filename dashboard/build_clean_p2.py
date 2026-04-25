#!/usr/bin/env python3
"""Part 2 - append remainder of HTML + JS to ops.html"""
import os

OUT = '/opt/itgyani-dashboard/frontend/ops.html'

PART2 = '''      <div class="p-2 flex items-center justify-between" style="border-bottom:1px solid #1f2d40">
        <span style="font-size:.72rem;color:#6b7280;font-weight:700;text-transform:uppercase">ACCOUNTS</span>
        <button class="btn btn-g text-xs px-2" onclick="syncEmail()">sync</button>
      </div>
      <div class="sy flex-1 p-1" id="acct-list"><div style="color:#6b7280;font-size:.78rem;padding:12px"><span class="spin"></span></div></div>
    </div>
    <div style="width:260px;border-right:1px solid #1f2d40;display:flex;flex-direction:column">
      <div class="p-2 flex items-center justify-between" style="border-bottom:1px solid #1f2d40">
        <span style="font-size:.72rem;color:#6b7280;font-weight:700;text-transform:uppercase" id="inbox-label">INBOX</span>
        <div class="flex gap-1">
          <button class="btn btn-g text-xs px-2" onclick="mailPage(-1)">prev</button>
          <button class="btn btn-g text-xs px-2" onclick="mailPage(1)">next</button>
        </div>
      </div>
      <div class="sy flex-1" id="email-list"><div style="color:#6b7280;font-size:.78rem;padding:16px;text-align:center">Select an account</div></div>
    </div>
    <div class="flex-1 flex flex-col overflow-hidden">
      <div id="reader-empty" class="flex-1 flex items-center justify-center" style="color:#374151;font-size:.9rem">Select an email to read</div>
      <div id="reader-content" class="hidden flex-1 flex flex-col overflow-hidden">
        <div class="p-3" style="border-bottom:1px solid #1f2d40">
          <div id="r-subject" class="text-white font-semibold text-sm mb-1"></div>
          <div id="r-meta" style="color:#6b7280;font-size:.75rem"></div>
        </div>
        <div class="sy flex-1 p-3"><div id="r-body" style="color:#cbd5e1;font-size:.85rem;line-height:1.6"></div></div>
        <div class="p-3" style="border-top:1px solid #1f2d40">
          <div id="reply-area" class="hidden">
            <textarea id="reply-txt" class="w-full mb-2" rows="3" placeholder="Write reply..." style="resize:vertical"></textarea>
            <div class="flex gap-2"><button class="btn btn-p text-xs" onclick="sendReply()">Send Reply</button><button class="btn btn-g text-xs" onclick="cancelReply()">Cancel</button></div>
          </div>
          <div id="reply-btns" class="flex gap-2">
            <button class="btn btn-p text-xs" onclick="showReply()">Reply</button>
            <button class="btn btn-r text-xs" onclick="deleteEmail()">Delete</button>
          </div>
        </div>
      </div>
      <div id="mail-login" class="hidden flex-1 flex flex-col items-center justify-center gap-3 p-6" style="text-align:center">
        <div style="font-size:2rem">&#128274;</div>
        <div class="text-white font-semibold">Login Required</div>
        <input id="ml-user" placeholder="Username" value="ashish" style="width:220px;text-align:center"/>
        <input id="ml-pass" type="password" placeholder="Password" style="width:220px;text-align:center"/>
        <button class="btn btn-p" onclick="mailLogin()">Unlock Mailbox</button>
        <div id="ml-err" class="hidden" style="color:#f87171;font-size:.78rem">Wrong credentials</div>
      </div>
    </div>
  </div>
</div>

<div id="tp-tasks" class="tp hidden">
  <div class="card p-3 mb-3">
    <div class="sec">Dispatch Task to Agent</div>
    <div class="flex flex-wrap gap-2">
      <input id="t-title" placeholder="Task title..." style="flex:1;min-width:200px"/>
      <select id="t-agent" style="min-width:120px"><option>RONY</option><option>MAYA</option><option>ARJUN</option><option>PRIYA</option><option>ZARA</option><option>FELIX</option><option>DISHA</option><option>KABIR</option><option>NIKKI</option><option>VIKRAM</option><option>ROHAN</option><option>TARA</option><option>KIRAN</option><option>RAVI</option></select>
      <select id="t-prio" style="min-width:100px"><option value="high">High</option><option value="med" selected>Med</option><option value="low">Low</option></select>
      <button class="btn btn-p" onclick="addTask()">+ Dispatch</button>
    </div>
  </div>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
    <div class="kcol"><div class="flex items-center justify-between mb-2"><div class="sec mb-0" style="color:#60a5fa">TO DO</div><span style="font-size:.72rem;color:#60a5fa" id="cnt-todo">0</span></div><div id="col-todo"></div></div>
    <div class="kcol"><div class="flex items-center justify-between mb-2"><div class="sec mb-0" style="color:#fb923c">IN PROGRESS</div><span style="font-size:.72rem;color:#fb923c" id="cnt-doing">0</span></div><div id="col-doing"></div></div>
    <div class="kcol"><div class="flex items-center justify-between mb-2"><div class="sec mb-0" style="color:#4ade80">DONE</div><span style="font-size:.72rem;color:#4ade80" id="cnt-done">0</span></div><div id="col-done"></div></div>
  </div>
</div>

<div id="tp-sprint" class="tp hidden">
  <div class="card p-4">
    <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
      <div>
        <div class="text-white font-semibold">Sprint 1 - Week1 Foundation</div>
        <div id="sprint-meta" style="color:#6b7280;font-size:.78rem">Loading from Jira...</div>
      </div>
      <div class="flex gap-1 flex-wrap">
        <a href="https://itgyani.atlassian.net/jira/software/projects/IT/boards/7" target="_blank" class="btn btn-g text-xs">IT</a>
        <a href="https://itgyani.atlassian.net/jira/software/projects/CG/boards" target="_blank" class="btn btn-g text-xs">CG</a>
        <a href="https://itgyani.atlassian.net/jira/software/projects/YUKTI/boards" target="_blank" class="btn btn-g text-xs">YUKTI</a>
        <a href="https://itgyani.atlassian.net/jira/software/projects/TEF/boards" target="_blank" class="btn btn-g text-xs">TEF</a>
        <a href="https://itgyani.atlassian.net/jira/software/projects/KO/boards" target="_blank" class="btn btn-g text-xs">KO</a>
        <a href="https://itgyani.atlassian.net/jira/software/projects/QPF/boards" target="_blank" class="btn btn-g text-xs">QPF</a>
        <a href="https://itgyani.atlassian.net/jira/software/projects/SF/boards" target="_blank" class="btn btn-g text-xs">SF</a>
      </div>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
      <div><div class="sec" style="color:#60a5fa">TO DO</div><div class="sy" style="max-height:420px" id="j-todo"></div></div>
      <div><div class="sec" style="color:#fb923c">IN PROGRESS</div><div class="sy" style="max-height:420px" id="j-prog"></div></div>
      <div><div class="sec" style="color:#4ade80">DONE</div><div class="sy" style="max-height:420px" id="j-done"></div></div>
    </div>
  </div>
</div>

<div id="tp-systems" class="tp hidden">
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    <div class="card p-4"><div class="sec">Containers</div><div id="sys-c" class="space-y-2"><div style="color:#6b7280;font-size:.85rem"><span class="spin"></span> Loading...</div></div></div>
    <div class="card p-4">
      <div class="sec">Quick Links</div>
      <div class="grid grid-cols-2 gap-1.5" style="font-size:.78rem">
        <a href="https://dashboard.itgyani.com" target="_blank" class="card2 p-2 text-center" style="text-decoration:none">Email Dashboard</a>
        <a href="https://n8n.itgyani.com" target="_blank" class="card2 p-2 text-center" style="text-decoration:none">n8n Workflows</a>
        <a href="https://openalgo.cryptogyani.com/python" target="_blank" class="card2 p-2 text-center" style="text-decoration:none">OpenAlgo</a>
        <a href="https://chartink.com/alert_dashboard" target="_blank" class="card2 p-2 text-center" style="text-decoration:none">ChartInk Alerts</a>
        <a href="https://cryptogyani.com" target="_blank" class="card2 p-2 text-center" style="text-decoration:none">CryptoGyani</a>
        <a href="https://itgyani.com" target="_blank" class="card2 p-2 text-center" style="text-decoration:none">ITGYANI.com</a>
        <a href="https://learn.theemployeefactory.com" target="_blank" class="card2 p-2 text-center" style="text-decoration:none">OpenMAIC LMS</a>
        <a href="https://kharadionline.com" target="_blank" class="card2 p-2 text-center" style="text-decoration:none">Kharadi Online</a>
        <a href="https://itgyani.atlassian.net" target="_blank" class="card2 p-2 text-center" style="text-decoration:none">Jira All Projects</a>
        <a href="https://github.com/shaashish1/open-claw-rony" target="_blank" class="card2 p-2 text-center" style="text-decoration:none">GitHub Repo</a>
      </div>
    </div>
  </div>
</div>

<div id="tp-logs" class="tp hidden">
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    <div class="card p-4">
      <div class="flex items-center justify-between mb-2">
        <div class="sec mb-0">Live Activity Log</div>
        <button class="btn btn-g text-xs" onclick="actLogs=[];renderLogs()">Clear</button>
      </div>
      <div class="sy" style="max-height:400px" id="live-log"><div style="color:#374151;font-size:.85rem;text-align:center;padding:32px">Activity appears here</div></div>
    </div>
    <div class="card p-4">
      <div class="flex items-center justify-between mb-2">
        <div class="sec mb-0">Minutes of Meeting</div>
        <button class="btn btn-p text-xs" onclick="document.getElementById('mom-frm').classList.toggle('hidden')">+ Add MOM</button>
      </div>
      <div id="mom-frm" class="hidden space-y-2 mb-3">
        <input id="mom-t" placeholder="Meeting title..." style="width:100%"/>
        <textarea id="mom-n" placeholder="Key decisions..." rows="3" style="width:100%;resize:vertical"></textarea>
        <div class="flex gap-2">
          <button class="btn btn-p flex-1 text-xs" onclick="saveMOM()">Save</button>
          <button class="btn btn-g flex-1 text-xs" onclick="document.getElementById('mom-frm').classList.add('hidden')">Cancel</button>
        </div>
      </div>
      <div class="sy" style="max-height:340px" id="mom-list"><div style="color:#374151;font-size:.85rem;text-align:center;padding:24px">No meetings yet.</div></div>
    </div>
  </div>
</div>

<div style="text-align:center;color:#374151;font-size:.72rem;margin-top:16px;padding-bottom:8px">
  ITGYANI OS v3 &mdash; Rony COO &mdash; Auto-refresh in <span id="cdtmr">15</span>m
</div>

<script>
// ========== SINGLE TAB FUNCTION (no duplicates) ==========
function switchTab(id, el) {
  document.querySelectorAll('.tp').forEach(function(t) { t.classList.add('hidden'); });
  document.querySelectorAll('.nav-tab').forEach(function(t) { t.classList.remove('active'); });
  var panel = document.getElementById('tp-' + id);
  if (panel) panel.classList.remove('hidden');
  if (el) el.classList.add('active');
  if (id === 'mailbox') initMail();
  if (id === 'sprint') loadSprint();
  if (id === 'systems') loadSys();
  if (id === 'logs') { loadMOM(); renderLogs(); }
}

// ========== CLOCK ==========
function tickClock() {
  var el = document.getElementById('clock');
  if (el) el.textContent = new Date().toLocaleTimeString('en-IN', {timeZone:'Asia/Calcutta', hour12:true});
}
setInterval(tickClock, 1000); tickClock();

// ========== AUTO REFRESH (15 minutes) ==========
var countdown = 15;
setInterval(function() {
  countdown--;
  var el = document.getElementById('cdtmr');
  if (el) el.textContent = countdown > 0 ? countdown : '...';
  if (countdown <= 0) { countdown = 15; loadAll(); }
}, 60000);

// ========== ACTIVITY LOG ==========
var actLogs = [];
function addLog(msg, type) {
  type = type || 'b';
  var now = new Date().toLocaleTimeString('en-IN', {timeZone:'Asia/Calcutta', hour12:true});
  actLogs.unshift({msg:msg, type:type, time:now});
  if (actLogs.length > 60) actLogs.pop();
  renderLogs();
}
function renderLogs() {
  var el = document.getElementById('live-log');
  if (!el) return;
  if (!actLogs.length) { el.innerHTML = '<div style="color:#374151;text-align:center;padding:32px">No activity yet</div>'; return; }
  var colors = {g:'#166534', o:'#9a3412', r:'#991b1b', b:'#3730a3'};
  el.innerHTML = actLogs.slice(0,50).map(function(l) {
    return '<div style="padding:7px 10px;border-left:2px solid '+(colors[l.type]||colors.b)+';margin-bottom:5px;font-size:.78rem"><span style="color:#4b5563">'+l.time+'</span><span style="color:#cbd5e1;margin-left:8px">'+l.msg+'</span></div>';
  }).join('');
}

// ========== STATUS API ==========
async function loadSys() {
  try {
    var r = await fetch('/api/ops/status', {cache:'no-store'});
    if (!r.ok) throw new Error('HTTP '+r.status);
    var d = await r.json();
    var sr = d.strategies || {};
    var run = sr.running !== undefined ? sr.running : 10;
    var conf = sr.configured !== undefined ? sr.configured : 10;
    document.getElementById('k-s').textContent = run+'/'+conf;
    document.getElementById('k-s-b').style.width = (conf > 0 ? (run/conf*100) : 100)+'%';
    document.getElementById('k-c').textContent = (d.chartink && d.chartink.total) || 15;
    var cc = document.getElementById('sys-c');
    cc.innerHTML = '';
    (d.containers || []).forEach(function(c) {
      cc.innerHTML += '<div style="display:flex;align-items:center;justify-content:space-between;padding:8px;background:#1a2235;border:1px solid #1f2d40;border-radius:6px;margin-bottom:4px">'
        +'<div><div style="color:#e2e8f0;font-size:.85rem">'+c.name+'</div><div style="color:#6b7280;font-size:.72rem">'+c.status.substring(0,40)+'</div></div>'
        +'<div style="display:flex;align-items:center;gap:4px"><div class="dot pulse" style="background:'+(c.ok?'#4ade80':'#f87171')+'"></div>'
        +'<span style="font-size:.75rem;color:'+(c.ok?'#4ade80':'#f87171')+'">'+(c.ok?'Up':'Down')+'</span></div></div>';
    });
    var ts = new Date(d.timestamp || Date.now()).toLocaleTimeString('en-IN', {timeZone:'Asia/Calcutta', hour12:true});
    document.getElementById('sync-lbl').textContent = 'Synced '+ts;
    addLog('Systems: '+run+'/'+conf+' strategies, '+(d.containers||[]).length+' containers', 'g');
  } catch(e) {
    document.getElementById('sync-lbl').textContent = 'API error';
    document.getElementById('k-s').textContent = '10/10';
    document.getElementById('k-c').textContent = '15';
    addLog('Status API error: '+e.message, 'r');
  }
}

// ========== JIRA SPRINT ==========
async function loadSprint() {
  try {
    var r = await fetch('/api/ops/jira-sprint', {cache:'no-store'});
    if (!r.ok) throw new Error('HTTP '+r.status);
    var d = await r.json();
    var dn = d.done||0, tot = d.total||0, ip = d.in_progress||0;
    document.getElementById('k-j').textContent = dn+'/'+tot;
    document.getElementById('k-j-l').textContent = dn+' done / '+tot+' issues';
    document.getElementById('sprint-meta').textContent = tot+' issues — '+dn+' done — '+ip+' in progress — '+(tot-dn-ip)+' to do';
    var jt = document.getElementById('j-todo');
    var jp = document.getElementById('j-prog');
    var jd = document.getElementById('j-done');
    jt.innerHTML = ''; jp.innerHTML = ''; jd.innerHTML = '';
    (d.issues || []).forEach(function(i) {
      var cat = i.status_cat || 'new';
      var card = '<div style="background:#1a2235;border:1px solid #1f2d40;border-radius:6px;padding:8px;margin-bottom:6px;font-size:.78rem">'
        +'<a href="https://itgyani.atlassian.net/browse/'+i.key+'" target="_blank" style="color:#818cf8;font-weight:700;text-decoration:none">'+i.key+'</a>'
        +'<div style="color:#cbd5e1;margin-top:3px;line-height:1.4">'+i.summary+'</div></div>';
      if (cat==='done') jd.innerHTML += card;
      else if (cat==='indeterminate') jp.innerHTML += card;
      else jt.innerHTML += card;
    });
    if (!jt.innerHTML) jt.innerHTML = '<div style="color:#374151;font-size:.75rem;text-align:center;padding:8px">Empty</div>';
    if (!jp.innerHTML) jp.innerHTML = '<div style="color:#374151;font-size:.75rem;text-align:center;padding:8px">Empty</div>';
    if (!jd.innerHTML) jd.innerHTML = '<div style="color:#374151;font-size:.75rem;text-align:center;padding:8px">Empty</div>';
    addLog('Sprint: '+tot+' issues, '+dn+' done', 'b');
  } catch(e) {
    document.getElementById('sprint-meta').textContent = 'Jira error: '+e.message;
    addLog('Jira error: '+e.message, 'r');
  }
}

// ========== MAILBOX ==========
var mailState = {acct: null, page: 1, uid: null};
async function initMail() {
  try {
    var r = await fetch('/api/accounts');
    if (r.status === 401 || r.status === 403) { showMailLogin(); return; }
    var a = await r.json();
    if (!Array.isArray(a)) { showMailLogin(); return; }
    renderAccts(a);
    if (a.length > 0 && !mailState.acct) selAcct(a[0].email, a[0].label);
  } catch(e) { showMailLogin(); }
}
function showMailLogin() {
  document.getElementById('acct-list').innerHTML = '<div style="color:#6b7280;font-size:.78rem;padding:8px">Login required</div>';
  document.getElementById('email-list').innerHTML = '';
  document.getElementById('reader-empty').classList.remove('hidden');
  document.getElementById('reader-content').classList.add('hidden');
  document.getElementById('mail-login').classList.remove('hidden');
}
async function mailLogin() {
  var fd = new FormData();
  fd.append('username', document.getElementById('ml-user').value);
  fd.append('password', document.getElementById('ml-pass').value);
  document.getElementById('ml-err').classList.add('hidden');
  try {
    await fetch('/login', {method:'POST', body:fd, redirect:'follow'});
    var r = await fetch('/api/accounts');
    if (r.ok) {
      document.getElementById('mail-login').classList.add('hidden');
      var a = await r.json();
      renderAccts(a);
      if (a.length > 0) selAcct(a[0].email, a[0].label);
      addLog('Mailbox unlocked', 'g');
    } else {
      document.getElementById('ml-err').classList.remove('hidden');
    }
  } catch(e) { document.getElementById('ml-err').classList.remove('hidden'); }
}
function renderAccts(a) {
  var el = document.getElementById('acct-list');
  el.innerHTML = '';
  a.forEach(function(x) {
    var u = x.unread || 0;
    var item = document.createElement('div');
    item.className = 'acc-item flex items-center justify-between';
    item.dataset.email = x.email;
    item.onclick = function() { selAcct(x.email, x.label || x.email); };
    item.innerHTML = '<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+(x.label||x.email.split('@')[0])+'</span>'
      +(u>0?'<span style="font-size:.7rem;background:#312e81;color:#a5b4fc;padding:1px 6px;border-radius:8px;flex-shrink:0">'+(u>99?'99+':u)+'</span>':'');
    el.appendChild(item);
  });
}
async function selAcct(email, label) {
  mailState.acct = email; mailState.page = 1; mailState.uid = null;
  document.getElementById('inbox-label').textContent = (label||email).toUpperCase();
  document.querySelectorAll('.acc-item').forEach(function(el) { el.classList.toggle('active', el.dataset.email === email); });
  await loadEmails();
}
async function loadEmails() {
  if (!mailState.acct) return;
  var el = document.getElementById('email-list');
  el.innerHTML = '<div style="color:#6b7280;font-size:.78rem;padding:16px;text-align:center"><span class="spin"></span></div>';
  try {
    var r = await fetch('/api/emails?account='+encodeURIComponent(mailState.acct)+'&page='+mailState.page+'&limit=20');
    if (r.status===401) { showMailLogin(); return; }
    var d = await r.json();
    var emails = d.emails || [];
    el.innerHTML = '';
    if (!emails.length) { el.innerHTML = '<div style="color:#6b7280;font-size:.78rem;padding:16px;text-align:center">No emails</div>'; return; }
    emails.forEach(function(e) {
      var from = (e.from_addr||'').replace(/<[^>]+>/g,'').trim().split('@')[0].substring(0,18);
      var subj = (e.subject||'(no subject)').substring(0,40);
      var date = e.date_str ? e.date_str.substring(0,10) : '';
      var row = document.createElement('div');
      row.className = 'erow' + (!e.is_read ? ' unread' : '');
      row.onclick = function() { openEmail(e.uid||e.id); };
      row.innerHTML = '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:2px">'
        +'<span style="color:#cbd5e1;font-size:.75rem;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+from+'</span>'
        +'<span style="color:#4b5563;font-size:.7rem;flex-shrink:0">'+date+'</span></div>'
        +'<div class="esub" style="color:#6b7280;font-size:.75rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+subj+'</div>';
      el.appendChild(row);
    });
  } catch(e) { el.innerHTML = '<div style="color:#f87171;font-size:.78rem;padding:12px">Error: '+e.message+'</div>'; }
}
async function openEmail(uid) {
  mailState.uid = uid;
  document.getElementById('reader-empty').classList.add('hidden');
  document.getElementById('mail-login').classList.add('hidden');
  document.getElementById('reader-content').classList.remove('hidden');
  document.getElementById('r-subject').textContent = 'Loading...';
  document.getElementById('r-body').innerHTML = '<span class="spin"></span>';
  cancelReply();
  try {
    var r = await fetch('/api/emails/'+encodeURIComponent(mailState.acct)+'/'+uid);
    var d = await r.json();
    var e = d.email || d;
    document.getElementById('r-subject').textContent = e.subject || '(no subject)';
    document.getElementById('r-meta').textContent = 'From: '+(e.from_addr||'')+' | '+(e.date_str||'');
    if (e.body_html) {
      document.getElementById('r-body').innerHTML = '<iframe srcdoc="'+e.body_html.replace(/"/g,'&quot;')+'" style="width:100%;height:280px;border:none;background:#fff;border-radius:4px"></iframe>';
    } else {
      document.getElementById('r-body').textContent = e.body_text || '(empty)';
    }
  } catch(e) { document.getElementById('r-body').textContent = 'Failed: '+e.message; }
}
function showReply() { document.getElementById('reply-area').classList.remove('hidden'); document.getElementById('reply-btns').classList.add('hidden'); document.getElementById('reply-txt').focus(); }
function cancelReply() { document.getElementById('reply-area').classList.add('hidden'); document.getElementById('reply-btns').classList.remove('hidden'); document.getElementById('reply-txt').value=''; }
async function sendReply() {
  var txt = document.getElementById('reply-txt').value.trim();
  if (!txt || !confirm('Send this reply?')) return;
  try {
    await fetch('/api/emails/'+encodeURIComponent(mailState.acct)+'/'+mailState.uid+'/send-reply', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({reply_text:txt})});
    cancelReply(); addLog('Reply sent','g'); alert('Sent!');
  } catch(e) { alert('Failed: '+e.message); }
}
async function deleteEmail() {
  if (!confirm('Move to Trash?')) return;
  try {
    await fetch('/api/emails/'+encodeURIComponent(mailState.acct)+'/'+mailState.uid, {method:'DELETE'});
    document.getElementById('reader-empty').classList.remove('hidden');
    document.getElementById('reader-content').classList.add('hidden');
    loadEmails(); addLog('Email deleted','o');
  } catch(e) { alert('Delete failed: '+e.message); }
}
function mailPage(d) { mailState.page = Math.max(1, mailState.page+d); loadEmails(); }
async function syncEmail() {
  try { await fetch('/api/sync/quick', {method:'POST'}); addLog('Email sync triggered','b'); setTimeout(function(){if(mailState.acct)loadEmails();},3000); } catch(e){}
}

// ========== TASKS (localStorage) ==========
function getTasks() { try {