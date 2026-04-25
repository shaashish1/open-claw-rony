"""Build ops.html — complete self-contained file"""
import os

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ITGYANI OS v3 — Command Center</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
*{box-sizing:border-box}
body{background:#0b0f1a;color:#e2e8f0;font-family:system-ui,-apple-system,sans-serif;min-height:100vh;margin:0}
.card{background:#111827;border:1px solid #1f2d40;border-radius:10px}
.card2{background:#1a2235;border:1px solid #1f2d40;border-radius:8px}
.nav-tab{padding:7px 14px;border-radius:6px;cursor:pointer;font-size:.8rem;font-weight:600;color:#6b7280;transition:all .15s;white-space:nowrap}
.nav-tab.active{background:#1e293b;color:#e2e8f0}
.nav-tab:hover:not(.active){color:#94a3b8}
.sec{font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:#4b5563;font-weight:700;margin-bottom:8px}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block;flex-shrink:0}
.dot-g{background:#4ade80}.dot-o{background:#fb923c}.dot-b{background:#818cf8}.dot-r{background:#f87171}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.pulse{animation:pulse 2s infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.spin{width:12px;height:12px;border:2px solid #1f2d40;border-top-color:#6366f1;border-radius:50%;animation:spin .8s linear infinite;display:inline-block;vertical-align:middle}
.pb{height:4px;background:#1f2d40;border-radius:2px;overflow:hidden;margin-top:6px}
.pf{height:100%;border-radius:2px;transition:width .6s}
.pf-g{background:linear-gradient(90deg,#16a34a,#4ade80)}
.pf-b{background:linear-gradient(90deg,#4f46e5,#818cf8)}
.pf-o{background:linear-gradient(90deg,#ea580c,#fb923c)}
a{color:#818cf8}a:hover{color:#a5b4fc}
input,textarea,select{background:#0b0f1a;border:1px solid #1f2d40;border-radius:6px;color:#e2e8f0;padding:7px 11px;font-size:.85rem;outline:none}
input:focus,textarea:focus,select:focus{border-color:#6366f1}
.btn{padding:6px 14px;border-radius:6px;font-size:.8rem;font-weight:600;cursor:pointer;border:none;transition:opacity .15s}
.btn:hover{opacity:.85}
.btn-p{background:#4f46e5;color:#fff}
.btn-g{background:#1a2235;color:#94a3b8;border:1px solid #1f2d40}
.btn-r{background:#7f1d1d;color:#fca5a5;border:1px solid #991b1b}
.sy{overflow-y:auto;scrollbar-width:thin;scrollbar-color:#1f2d40 transparent}
.badge{display:inline-flex;align-items:center;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:20px}
.b-live{background:#052e16;color:#4ade80;border:1px solid #166534}
.b-build{background:#1c1917;color:#fb923c;border:1px solid #9a3412}
.b-plan{background:#1e1b4b;color:#818cf8;border:1px solid #3730a3}
.b-hi{background:#450a0a;color:#f87171;border:1px solid #991b1b}
.b-med{background:#1c1917;color:#fbbf24;border:1px solid #92400e}
.b-lo{background:#111827;color:#6b7280;border:1px solid #374151}
.ring-wrap{position:relative;width:52px;height:52px;flex-shrink:0}
.ring-svg{transform:rotate(-90deg)}
.ring-bg{fill:none;stroke:#1f2d40;stroke-width:5}
.ring-fg{fill:none;stroke-width:5;stroke-linecap:round}
.ring-lbl{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:700}
.acc-item{padding:8px 12px;cursor:pointer;border-radius:6px;font-size:.82rem;transition:background .1s}
.acc-item:hover{background:#1a2235}
.acc-item.active{background:#1e2d40;color:#818cf8}
.email-row{padding:10px 12px;cursor:pointer;border-bottom:1px solid #1f2d40;font-size:.82rem}
.email-row:hover{background:#1a2235}
.email-row.unread .e-subj{font-weight:700;color:#e2e8f0}
.task-card{padding:10px;border-radius:6px;background:#1a2235;border:1px solid #1f2d40;margin-bottom:6px;cursor:pointer}
.task-card:hover{border-color:#374151}
.done-card{opacity:.4}
.kcol{background:#111827;border:1px solid #1f2d40;border-radius:8px;padding:10px;min-height:160px}
.proj-card{background:#111827;border:1px solid #1f2d40;border-radius:10px;padding:14px}
.proj-card:hover{border-color:#374151}
</style>
</head>
<body class="p-3 md:p-4">

<div class="flex items-center justify-between mb-3 flex-wrap gap-2">
  <div class="flex items-center gap-2">
    <div class="dot dot-g pulse"></div>
    <span class="text-white font-bold text-sm">ITGYANI OS v3</span>
    <span class="text-xs px-2 py-0.5 rounded-full bg-indigo-900/40 text-indigo-300 border border-indigo-700/40">Command Center</span>
  </div>
  <div class="flex items-center gap-3">
    <div class="text-right hidden sm:block">
      <div id="clock" class="text-white font-mono font-bold text-sm"></div>
      <div id="sync-lbl" class="text-slate-500 text-xs">Syncing...</div>
    </div>
    <button class="btn btn-g text-xs" onclick="loadAll()">&#8635; Refresh</button>
    <a href="https://itgyani.atlassian.net/jira/software/projects/IT/boards/7" target="_blank" class="btn btn-p text-xs">Jira Board</a>
  </div>
</div>

<div class="grid grid-cols-2 md:grid-cols-6 gap-2 mb-3">
  <div class="card p-3"><div class="sec">Revenue MTD</div><div class="text-xl font-bold text-white">&#8377;0</div><div class="text-xs text-slate-500 mt-0.5">Target &#8377;1L/mo</div><div class="pb"><div class="pf pf-b" style="width:1%"></div></div></div>
  <div class="card p-3"><div class="sec">Strategies</div><div id="k-s" class="text-xl font-bold text-green-400"><span class="spin"></span></div><div class="text-xs text-slate-500 mt-0.5">Analyze mode</div><div class="pb"><div class="pf pf-g" id="k-s-b" style="width:0%"></div></div></div>
  <div class="card p-3"><div class="sec">ChartInk Alerts</div><div id="k-c" class="text-xl font-bold text-green-400"><span class="spin"></span></div><div class="text-xs text-slate-500 mt-0.5">to OpenAlgo</div><div class="pb"><div class="pf pf-g" style="width:100%"></div></div></div>
  <div class="card p-3"><div class="sec">Sprint 1</div><div id="k-j" class="text-xl font-bold text-white"><span class="spin"></span></div><div id="k-j-l" class="text-xs text-slate-500 mt-0.5">stories</div><div class="pb"><div class="pf pf-b" id="k-j-b" style="width:0%"></div></div></div>
  <div class="card p-3"><div class="sec">Agents Live</div><div class="text-xl font-bold text-indigo-400">10<span class="text-slate-500 text-sm">/14</span></div><div class="text-xs text-slate-500 mt-0.5">4 building/planned</div><div class="pb"><div class="pf pf-b" style="width:71%"></div></div></div>
  <div class="card p-3"><div class="sec">Projects</div><div class="text-xl font-bold text-yellow-400">8</div><div class="text-xs text-slate-500 mt-0.5">5 Active / 3 Planned</div><div class="pb"><div class="pf pf-o" style="width:63%"></div></div></div>
</div>

<div class="flex gap-1 mb-3 bg-slate-900/40 p-1 rounded-lg overflow-x-auto">
  <div class="nav-tab active" onclick="tab('agents',this)">Agents</div>
  <div class="nav-tab" onclick="tab('projects',this)">Projects</div>
  <div class="nav-tab" onclick="tab('mailbox',this)">Mailbox</div>
  <div class="nav-tab" onclick="tab('tasks',this)">Tasks</div>
  <div class="nav-tab" onclick="tab('sprint',this)">Sprint</div>
  <div class="nav-tab" onclick="tab('systems',this)">Systems</div>
  <div class="nav-tab" onclick="tab('logs',this)">Logs</div>
</div>

<div id="tp-agents" class="tp">
  <div class="sec mb-3 text-slate-400">Performance and Utilization Report - All 14 Agents</div>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3" id="agents-grid"></div>
</div>

<div id="tp-projects" class="tp hidden">
  <div class="sec mb-3 text-slate-400">All Projects - Active + Planned (8 total | 135 Jira issues)</div>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3" id="projects-grid"></div>
</div>

<div id="tp-mailbox" class="tp hidden">
  <div class="card" style="height:calc(100vh - 230px);display:flex;overflow:hidden">
    <div style="width:200px;min-width:160px;border-right:1px solid #1f2d40;display:flex;flex-direction:column">
      <div class="p-2 border-b border-slate-800 flex items-center justify-between">
        <span class="text-xs text-slate-400 font-semibold">ACCOUNTS</span>
        <button class="btn btn-g text-xs px-2 py-0.5" onclick="syncEmail()">sync</button>
      </div>
      <div class="sy flex-1 p-1" id="acct-list"><div class="text-slate-500 text-xs p-3"><span class="spin"></span></div></div>
    </div>
    <div style="width:280px;min-width:220px;border-right:1px solid #1f2d40;display:flex;flex-direction:column">
      <div class="p-2 border-b border-slate-800 flex items-center justify-between">
        <span class="text-xs text-slate-400 font-semibold" id="inbox-label">INBOX</span>
        <div class="flex gap-1">
          <button class="btn btn-g text-xs px-2 py-0.5" onclick="mailPage(-1)">prev</button>
          <button class="btn btn-g text-xs px-2 py-0.5" onclick="mailPage(1)">next</button>
        </div>
      </div>
      <div class="sy flex-1" id="email-list"><div class="text-slate-500 text-xs p-4 text-center">Select an account</div></div>
    </div>
    <div class="flex-1 flex flex-col overflow-hidden">
      <div id="reader-empty" class="flex-1 flex items-center justify-center text-slate-600 text-sm">Select an email to read</div>
      <div id="reader-content" class="hidden flex-1 flex flex-col overflow-hidden">
        <div class="p-3 border-b border-slate-800">
          <div id="r-subject" class="text-white font-semibold text-sm mb-1"></div>
          <div id="r-meta" class="text-slate-500 text-xs"></div>
        </div>
        <div class="sy flex-1 p-3"><div id="r-body" class="text-slate-300 text-sm leading-relaxed"></div></div>
        <div class="p-3 border-t border-slate-800">
          <div id="reply-area" class="hidden">
            <textarea id="reply-txt" class="w-full mb-2" rows="3" placeholder="Write reply..." style="resize:vertical"></textarea>
            <div class="flex gap-2">
              <button class="btn btn-p text-xs" onclick="sendReply()">Send Reply</button>
              <button class="btn btn-g text-xs" onclick="cancelReply()">Cancel</button>
            </div>
          </div>
          <div id="reply-btns" class="flex gap-2">
            <button class="btn btn-p text-xs" onclick="showReply()">Reply</button>
            <button class="btn btn-r text-xs" onclick="deleteEmail()">Delete</button>
          </div>
        </div>
      </div>
      <div id="mail-login-prompt" class="hidden flex-1 flex flex-col items-center justify-center gap-3 text-center p-6">
        <div class="text-3xl">&#128274;</div>
        <div class="text-white font-semibold">Login Required</div>
        <div class="text-slate-400 text-sm mb-2">Enter dashboard credentials to access mailbox.</div>
        <input id="ml-user" placeholder="Username" value="ashish" style="width:220px;text-align:center"/>
        <input id="ml-pass" type="password" placeholder="Password" style="width:220px;text-align:center"/>
        <button class="btn btn-p" onclick="mailLogin()">Unlock Mailbox</button>
        <div id="ml-err" class="text-red-400 text-xs hidden">Login failed</div>
      </div>
    </div>
  </div>
</div>

<div id="tp-tasks" class="tp hidden">
  <div class="card p-3 mb-3">
    <div class="sec">Dispatch Task</div>
    <div class="flex flex-wrap gap-2">
      <input id="t-title" placeholder="Task title..." style="flex:1;min-width:200px"/>
      <select id="t-agent" style="min-width:120px">
        <option>RONY</option><option>MAYA</option><option>ARJUN</option><option>PRIYA</option>
        <option>ZARA</option><option>FELIX</option><option>DISHA</option><option>KABIR</option>
        <option>NIKKI</option><option>VIKRAM</option><option>ROHAN</option><option>TARA</option>
        <option>KIRAN</option><option>RAVI</option>
      </select>
      <select id="t-prio" style="min-width:100px">
        <option value="high">High</option><option value="med" selected>Med</option><option value="low">Low</option>
      </select>
      <button class="btn btn-p" onclick="addTask()">+ Dispatch</button>
    </div>
  </div>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
    <div class="kcol"><div class="flex items-center justify-between mb-2"><div class="sec mb-0 text-blue-400">TO DO</div><span class="text-xs bg-blue-900/40 text-blue-400 px-2 rounded-full" id="cnt-todo">0</span></div><div id="col-todo"></div></div>
    <div class="kcol"><div class="flex items-center justify-between mb-2"><div class="sec mb-0 text-orange-400">IN PROGRESS</div><span class="text-xs bg-orange-900/40 text-orange-400 px-2 rounded-full" id="cnt-doing">0</span></div><div id="col-doing"></div></div>
    <div class="kcol"><div class="flex items-center justify-between mb-2"><div class="sec mb-0 text-green-400">DONE</div><span class="text-xs bg-green-900/40 text-green-400 px-2 rounded-full" id="cnt-done">0</span></div><div id="col-done"></div></div>
  </div>
</div>

<div id="tp-sprint" class="tp hidden">
  <div class="card p-4">
    <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
      <div>
        <div class="text-white font-semibold">Sprint 1 - Week1 Foundation</div>
        <div class="text-xs text-slate-500" id="sprint-meta">Loading from Jira...</div>
      </div>
      <div class="flex gap-2 flex-wrap">
        <a href="https://itgyani.atlassian.net/jira/software/projects/IT/boards/7" target="_blank" class="btn btn-g text-xs">IT Board</a>
        <a href="https://itgyani.atlassian.net/jira/software/projects/CG/boards" target="_blank" class="btn btn-g text-xs">CG Board</a>
        <a href="https://itgyani.atlassian.net/jira/software/projects/YUKTI/boards" target="_blank" class="btn btn-g text-xs">YUKTI</a>
        <a href="https://itgyani.atlassian.net/jira/software/projects/TEF/boards" target="_blank" class="btn btn-g text-xs">TEF</a>
        <a href="https://itgyani.atlassian.net/jira/software/projects/KO/boards" target="_blank" class="btn btn-g text-xs">KO</a>
      </div>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
      <div><div class="sec text-blue-400">TO DO</div><div class="sy" style="max-height:420px" id="j-todo"></div></div>
      <div><div class="sec text-orange-400">IN PROGRESS</div><div class="sy" style="max-height:420px" id="j-prog"></div></div>
      <div><div class="sec text-green-400">DONE</div><div class="sy" style="max-height:420px" id="j-done"></div></div>
    </div>
  </div>
</div>

<div id="tp-systems" class="tp hidden">
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    <div class="card p-4">
      <div class="sec">Containers</div>
      <div id="sys-c" class="space-y-2"><div class="text-slate-500 text-sm"><span class="spin"></span> Loading...</div></div>
    </div>
    <div class="card p-4">
      <div class="sec">Quick Links</div>
      <div class="grid grid-cols-2 gap-1.5">
        <a href="https://dashboard.itgyani.com" target="_blank" class="card2 p-2 text-xs text-center hover:border-indigo-700/50 transition-colors">Email Dashboard</a>
        <a href="https://n8n.itgyani.com" target="_blank" class="card2 p-2 text-xs text-center hover:border-indigo-700/50 transition-colors">n8n Workflows</a>
        <a href="https://openalgo.cryptogyani.com/python" target="_blank" class="card2 p-2 text-xs text-center hover:border-indigo-700/50 transition-colors">OpenAlgo</a>
        <a href="https://chartink.com/alert_dashboard" target="_blank" class="card2 p-2 text-xs text-center hover:border-indigo-700/50 transition-colors">ChartInk Alerts</a>
        <a href="https://cryptogyani.com" target="_blank" class="card2 p-2 text-xs text-center hover:border-indigo-700/50 transition-colors">CryptoGyani</a>
        <a href="https://itgyani.com" target="_blank" class="card2 p-2 text-xs text-center hover:border-indigo-700/50 transition-colors">ITGYANI.com</a>
        <a href="https://learn.theemployeefactory.com" target="_blank" class="card2 p-2 text-xs text-center hover:border-indigo-700/50 transition-colors">OpenMAIC LMS</a>
        <a href="https://kharadionline.com" target="_blank" class="card2 p-2 text-xs text-center hover:border-indigo-700/50 transition-colors">Kharadi Online</a>
        <a href="https://itgyani.atlassian.net" target="_blank" class="card2 p-2 text-xs text-center hover:border-indigo-700/50 transition-colors">Jira All Projects</a>
        <a href="https://github.com/shaashish1/open-claw-rony" target="_blank" class="card2 p-2 text-xs text-center hover:border-indigo-700/50 transition-colors">GitHub Repo</a>
      </div>
    </div>
  </div>
</div>

<div id="tp-logs" class="tp hidden">
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
    <div class="card p-4">
      <div class="flex items-center justify-between mb-2">
        <div class="sec mb-0">Live Activity Log</div>
        <button class="btn btn-g text-xs" onclick="logs=[];renderLogs()">Clear</button>
      </div>
      <div class="sy" style="max-height:400px" id="live-log"><div class="text-slate-600 text-sm text-center py-8">Activity will appear here</div></div>
    </div>
    <div class="card p-4">
      <div class="flex items-center justify-between mb-2">
        <div class="sec mb-0">Minutes of Meeting</div>
        <button class="btn btn-p text-xs" onclick="document.getElementById('mom-frm').classList.toggle('hidden')">+ Add MOM</button>
      </div>
      <div id="mom-frm" class="hidden space-y-2 mb-3">
        <input id="mom-t" placeholder="Meeting title..." style="width:100%"/>
        <textarea id="mom-n" placeholder="Key decisions and actions..." rows="3" style="width:100%;resize:vertical"></textarea>
        <div class="flex gap-2">
          <button class="btn btn-p flex-1 text-xs" onclick="saveMOM()">Save</button>
          <button class="btn btn-g flex-1 text-xs" onclick="document.getElementById('mom-frm').classList.add('hidden')">Cancel</button>
        </div>
      </div>
      <div class="sy" style="max-height:340px" id="mom-list"><div class="text-slate-600 text-sm text-center py-6">No meetings yet.</div></div>
    </div>
  </div>
</div>

<div class="text-center text-slate-700 text-xs mt-4 pb-2">
  ITGYANI OS v3 - Rony COO - Auto-refresh in <span id="cd">30</span>s
</div>

<script>
const AGENTS = [
  {name:"RONY",role:"COO",emoji:"R",status:"live",task:"Sprint oversight, agent coordination, blocker escalation",
   kpis:["Agents: 10/14","Sprint: 0/41","Blockers: 0"],util:72,model:"Sonnet",
   jira:[["IT-34","Add agent KPI tiles","IT-34"],["IT-35","QA all dashboard panels","IT-35"]]},
  {name:"MAYA",role:"CMO / Lead Gen",emoji:"M",status:"live",task:"Email cleanup 8,031 emails + 1M lead database build",
   kpis:["Emails: 0/8031","Leads: 0/50K","Campaigns: 0"],util:45,model:"Haiku",
   jira:[["IT-26","Audit 8031 emails","IT-26"],["IT-27","Email cleanup n8n workflow","IT-27"],["IT-28","Lead scraper 50K","IT-28"],["IT-30","SendGrid setup","IT-30"],["IT-31","First 50K campaign","IT-31"]]},
  {name:"ARJUN",role:"InfoSec & Compliance",emoji:"A",status:"build",task:"Security audit + job alert bot VPS deploy + RULE 0 enforcer",
   kpis:["Secrets: Clean","Alerts: 0 fired","Violations: 0"],util:30,model:"Sonnet",
   jira:[["YUKTI-7","Security audit OpenAlgo","YUKTI-7"],["IT-7","Freelancer outreach agent","IT-7"]]},
  {name:"PRIYA",role:"SEO Lead",emoji:"P",status:"live",task:"CryptoGyani SEO launch - 10 articles/week + keyword research",
   kpis:["Articles: 0/10","Keywords: 0/100","DA: N/A"],util:55,model:"Haiku",
   jira:[["CG-52","CryptoGyani SEO Launch","CG-52"],["CG-54","SEO audit meta tags","CG-54"],["CG-55","GA4 Search Console","CG-55"],["CG-56","Publish 10 SEO articles","CG-56"],["CG-59","Apply for AdSense","CG-59"]]},
  {name:"ZARA",role:"Sales & Cold Outreach",emoji:"Z",status:"live",task:"100 cold email prospects - fintech and SaaS founders",
   kpis:["Prospects: 0/100","Emails: 0 sent","Replies: 0"],util:20,model:"Haiku",
   jira:[["IT-15","ITGYANI First 5 Clients","IT-15"],["IT-21","Cold email 100 prospects","IT-21"],["IT-23","LinkedIn 50 DMs/day","IT-23"],["IT-24","Sales proposal template","IT-24"]]},
  {name:"FELIX",role:"Customer Support",emoji:"F",status:"plan",task:"50-FAQ SOP library + support bot setup",
   kpis:["FAQs: 0/50","Bot: Not live","Tickets: 0"],util:5,model:"Haiku",
   jira:[["IT-11","Customer support bot","IT-11"]]},
  {name:"DISHA",role:"Project Manager",emoji:"D",status:"live",task:"Sprint 1 daily standup + blocker escalation within 30min",
   kpis:["Blockers: 0","On-time: N/A","Sprint: At Risk"],util:40,model:"Haiku",
   jira:[["IT-1","Sprint 1 kickoff","IT-1"],["IT-12","Admin dashboard","IT-12"],["IT-13","Full automation test","IT-13"]]},
  {name:"KABIR",role:"DevOps",emoji:"K",status:"live",task:"VPS hardening + Fyers auto-login + n8n YouTube production",
   kpis:["Strategies: 10/10","Uptime: 99.9%","Disk: 62/391GB"],util:85,model:"Haiku",
   jira:[["YUKTI-3","Audit OpenAlgo config","YUKTI-3"],["YUKTI-4","Broker connections doc","YUKTI-4"],["IT-13","Full automation test","IT-13"]]},
  {name:"NIKKI",role:"Designer & UI QA",emoji:"N",status:"build",task:"ITGYANI service page + QA gate for all UI before ship",
   kpis:["QA Gate: Active","Pages: 0/3","Bugs: 0 found"],util:35,model:"Haiku",
   jira:[["IT-20","Service menu pricing page","IT-20"],["IT-4","Design service categories","IT-4"]]},
  {name:"VIKRAM",role:"Analytics",emoji:"V",status:"live",task:"Revenue KPI + daily P&L + ad performance dashboard",
   kpis:["Revenue: Rs 0","ROAS: N/A","Reports: 0/7"],util:50,model:"Haiku",
   jira:[["IT-33","AI model costs panel","IT-33"],["IT-36","Performance test dashboard","IT