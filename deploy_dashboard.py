#!/usr/bin/env python3
"""Deploy ITGYANI Operations Dashboard to dashboard.itgyani.com"""

import paramiko
import time

HOST = "194.233.64.74"
PORT = 22
USER = "rony"
PASSWORD = "Rony@ITGYANI2026#Secure"

MOM_JSON = '{"meetings":[]}'

NGINX_CONF = """server {
    listen 80;
    server_name dashboard.itgyani.com;
    root /var/www/dashboard;
    index index.html;
    location / {
        try_files $uri $uri/ =404;
    }
}
"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ITGYANI OS v3 — Operations Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background-color: #0f172a; font-family: system-ui, sans-serif; }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 0.75rem; }
    .card-inner { background: #162032; border: 1px solid #1e3a5f; border-radius: 0.6rem; }
    .badge-active { background: #064e3b; color: #34d399; border: 1px solid #059669; }
    .badge-standby { background: #1c1917; color: #a8a29e; border: 1px solid #57534e; }
    @keyframes pulse-green { 0%,100%{opacity:1} 50%{opacity:.5} }
    .pulse-active { animation: pulse-green 2s infinite; background: #34d399; box-shadow: 0 0 6px #34d399; }
    .pulse-standby { background: #78716c; }
    .section-title { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: #6366f1; }
    .sys-link { transition: all 0.15s; display: flex; align-items: center; justify-content: space-between; }
    .sys-link:hover { transform: translateY(-2px); }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    .progress-bar { height: 8px; background: #1e293b; border-radius: 4px; overflow: hidden; }
    .progress-fill { height: 100%; background: linear-gradient(90deg, #6366f1, #8b5cf6); border-radius: 4px; transition: width 1s ease; }
  </style>
</head>
<body class="min-h-screen text-slate-100">

<!-- HEADER -->
<header class="border-b border-slate-700/60 bg-slate-900/90 backdrop-blur sticky top-0 z-50">
  <div class="max-w-screen-xl mx-auto px-6 py-3 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-black text-sm select-none">IY</div>
      <div>
        <h1 class="text-base font-bold text-white tracking-tight">ITGYANI OS <span class="text-indigo-400">v3</span></h1>
        <p class="text-xs text-slate-400 -mt-0.5">Operations Dashboard</p>
      </div>
    </div>
    <div class="flex items-center gap-5">
      <div class="hidden md:flex items-center gap-2 text-xs text-slate-400">
        <span class="w-2 h-2 rounded-full pulse-active inline-block"></span>
        <span>Systems Nominal</span>
      </div>
      <div class="text-right">
        <div id="clock" class="text-sm font-mono font-semibold text-indigo-300">--:--:--</div>
        <div id="dateline" class="text-xs text-slate-500"></div>
      </div>
    </div>
  </div>
</header>

<main class="max-w-screen-xl mx-auto px-4 md:px-6 py-6 space-y-6">

  <!-- STAT BAR -->
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    <div class="card p-4 text-center">
      <div class="text-3xl font-black text-indigo-400">14</div>
      <div class="text-xs text-slate-400 mt-1 uppercase tracking-wider">Total Agents</div>
    </div>
    <div class="card p-4 text-center">
      <div class="text-3xl font-black text-emerald-400">11</div>
      <div class="text-xs text-slate-400 mt-1 uppercase tracking-wider">Active</div>
    </div>
    <div class="card p-4 text-center">
      <div class="text-3xl font-black text-amber-400">3</div>
      <div class="text-xs text-slate-400 mt-1 uppercase tracking-wider">Standby</div>
    </div>
    <div class="card p-4 text-center">
      <div class="text-3xl font-black text-violet-400">21</div>
      <div class="text-xs text-slate-400 mt-1 uppercase tracking-wider">Sprint Stories</div>
    </div>
  </div>

  <!-- SECTION 1: AGENT STATUS -->
  <div class="card p-5">
    <div class="flex items-center justify-between mb-4">
      <div>
        <p class="section-title">Section 01</p>
        <h2 class="text-lg font-bold text-white mt-0.5">Agent Status</h2>
      </div>
      <span class="text-xs text-slate-500 font-mono bg-slate-800 px-2 py-1 rounded">14 deployed</span>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
      <!-- RONY -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-indigo-900/60 flex items-center justify-center text-indigo-300 font-bold text-xs shrink-0">RY</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">RONY</span>
            <span class="badge-active text-xs px-2 py-0.5 rounded-full font-medium">Active</span>
          </div>
          <div class="text-xs text-indigo-400 font-medium mt-0.5">COO</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">Strategy &amp; Ops</div>
        </div>
      </div>
      <!-- MAYA -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-pink-900/60 flex items-center justify-center text-pink-300 font-bold text-xs shrink-0">MA</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">MAYA</span>
            <span class="badge-active text-xs px-2 py-0.5 rounded-full font-medium">Active</span>
          </div>
          <div class="text-xs text-pink-400 font-medium mt-0.5">CMO</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">Email Marketing</div>
        </div>
      </div>
      <!-- ARJUN -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-red-900/60 flex items-center justify-center text-red-300 font-bold text-xs shrink-0">AR</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">ARJUN</span>
            <span class="badge-active text-xs px-2 py-0.5 rounded-full font-medium">Active</span>
          </div>
          <div class="text-xs text-red-400 font-medium mt-0.5">InfoSec</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">Security Audit</div>
        </div>
      </div>
      <!-- PRIYA -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-emerald-900/60 flex items-center justify-center text-emerald-300 font-bold text-xs shrink-0">PR</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">PRIYA</span>
            <span class="badge-active text-xs px-2 py-0.5 rounded-full font-medium">Active</span>
          </div>
          <div class="text-xs text-emerald-400 font-medium mt-0.5">SEO Lead</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">CryptoGyani SEO</div>
        </div>
      </div>
      <!-- ZARA -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-orange-900/60 flex items-center justify-center text-orange-300 font-bold text-xs shrink-0">ZA</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">ZARA</span>
            <span class="badge-active text-xs px-2 py-0.5 rounded-full font-medium">Active</span>
          </div>
          <div class="text-xs text-orange-400 font-medium mt-0.5">Sales</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">Cold Outreach</div>
        </div>
      </div>
      <!-- FELIX -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-slate-700/60 flex items-center justify-center text-slate-300 font-bold text-xs shrink-0">FX</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">FELIX</span>
            <span class="badge-standby text-xs px-2 py-0.5 rounded-full font-medium">Standby</span>
          </div>
          <div class="text-xs text-slate-400 font-medium mt-0.5">Support</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">Customer Success</div>
        </div>
      </div>
      <!-- DISHA -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-violet-900/60 flex items-center justify-center text-violet-300 font-bold text-xs shrink-0">DI</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">DISHA</span>
            <span class="badge-active text-xs px-2 py-0.5 rounded-full font-medium">Active</span>
          </div>
          <div class="text-xs text-violet-400 font-medium mt-0.5">PM</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">Sprint 1 Tracking</div>
        </div>
      </div>
      <!-- KABIR -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-cyan-900/60 flex items-center justify-center text-cyan-300 font-bold text-xs shrink-0">KB</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">KABIR</span>
            <span class="badge-active text-xs px-2 py-0.5 rounded-full font-medium">Active</span>
          </div>
          <div class="text-xs text-cyan-400 font-medium mt-0.5">DevOps</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">VPS Infrastructure</div>
        </div>
      </div>
      <!-- NIKKI -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-slate-700/60 flex items-center justify-center text-slate-300 font-bold text-xs shrink-0">NK</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">NIKKI</span>
            <span class="badge-standby text-xs px-2 py-0.5 rounded-full font-medium">Standby</span>
          </div>
          <div class="text-xs text-slate-400 font-medium mt-0.5">Designer</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">UI/UX QA</div>
        </div>
      </div>
      <!-- VIKRAM -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-yellow-900/60 flex items-center justify-center text-yellow-300 font-bold text-xs shrink-0">VK</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">VIKRAM</span>
            <span class="badge-active text-xs px-2 py-0.5 rounded-full font-medium">Active</span>
          </div>
          <div class="text-xs text-yellow-400 font-medium mt-0.5">Analytics</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">Revenue Tracking</div>
        </div>
      </div>
      <!-- ROHAN -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-lime-900/60 flex items-center justify-center text-lime-300 font-bold text-xs shrink-0">RH</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">ROHAN</span>
            <span class="badge-active text-xs px-2 py-0.5 rounded-full font-medium">Active</span>
          </div>
          <div class="text-xs text-lime-400 font-medium mt-0.5">Finance</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">P&amp;L Dashboard</div>
        </div>
      </div>
      <!-- TARA -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-sky-900/60 flex items-center justify-center text-sky-300 font-bold text-xs shrink-0">TR</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">TARA</span>
            <span class="badge-active text-xs px-2 py-0.5 rounded-full font-medium">Active</span>
          </div>
          <div class="text-xs text-sky-400 font-medium mt-0.5">Research</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">Demand Validation</div>
        </div>
      </div>
      <!-- KIRAN -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-slate-700/60 flex items-center justify-center text-slate-300 font-bold text-xs shrink-0">KR</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">KIRAN</span>
            <span class="badge-standby text-xs px-2 py-0.5 rounded-full font-medium">Standby</span>
          </div>
          <div class="text-xs text-slate-400 font-medium mt-0.5">HR</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">Team Ops</div>
        </div>
      </div>
      <!-- RAVI -->
      <div class="card-inner p-3 flex items-start gap-3">
        <div class="w-9 h-9 rounded-lg bg-fuchsia-900/60 flex items-center justify-center text-fuchsia-300 font-bold text-xs shrink-0">RV</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1">
            <span class="font-semibold text-sm text-white">RAVI</span>
            <span class="badge-active text-xs px-2 py-0.5 rounded-full font-medium">Active</span>
          </div>
          <div class="text-xs text-fuchsia-400 font-medium mt-0.5">RevOps</div>
          <div class="text-xs text-slate-400 truncate mt-0.5">Razorpay Setup</div>
        </div>
      </div>
    </div>
  </div>

  <!-- SECTIONS 2 + 3 SIDE BY SIDE -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

    <!-- SECTION 2: SYSTEM HEALTH -->
    <div class="card p-5">
      <div class="mb-4">
        <p class="section-title">Section 02</p>
        <h2 class="text-lg font-bold text-white mt-0.5">System Health</h2>
      </div>
      <div class="space-y-2">
        <a href="https://openalgo.cryptogyani.com" target="_blank" rel="noopener" class="sys-link card-inner px-4 py-3 rounded-lg group hover:border-indigo-500 transition-colors">
          <div class="flex items-center gap-3">
            <span class="w-2 h-2 rounded-full pulse-active inline-block"></span>
            <div>
              <div class="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors">OpenAlgo</div>
              <div class="text-xs text-slate-500">Trading Platform</div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-emerald-400 font-medium">Online</span>
            <svg class="w-3.5 h-3.5 text-slate-600 group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
          </div>
        </a>
        <a href="https://n8n.itgyani.com" target="_blank" rel="noopener" class="sys-link card-inner px-4 py-3 rounded-lg group hover:border-indigo-500 transition-colors">
          <div class="flex items-center gap-3">
            <span class="w-2 h-2 rounded-full pulse-active inline-block"></span>
            <div>
              <div class="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors">n8n</div>
              <div class="text-xs text-slate-500">Automation Engine</div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-emerald-400 font-medium">Online</span>
            <svg class="w-3.5 h-3.5 text-slate-600 group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
          </div>
        </a>
        <a href="https://itgyani.atlassian.net" target="_blank" rel="noopener" class="sys-link card-inner px-4 py-3 rounded-lg group hover:border-indigo-500 transition-colors">
          <div class="flex items-center gap-3">
            <span class="w-2 h-2 rounded-full pulse-active inline-block"></span>
            <div>
              <div class="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors">Jira Sprint 1</div>
              <div class="text-xs text-slate-500">Task Board</div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-emerald-400 font-medium">Online</span>
            <svg class="w-3.5 h-3.5 text-slate-600 group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
          </div>
        </a>
        <a href="https://cryptogyani.com" target="_blank" rel="noopener" class="sys-link card-inner px-4 py-3 rounded-lg group hover:border-indigo-500 transition-colors">
          <div class="flex items-center gap-3">
            <span class="w-2 h-2 rounded-full pulse-active inline-block"></span>
            <div>
              <div class="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors">CryptoGyani</div>
              <div class="text-xs text-slate-500">cryptogyani.com</div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-emerald-400 font-medium">Online</span>
            <svg class="w-3.5 h-3.5 text-slate-600 group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
          </div>
        </a>
        <a href="https://itgyani.com" target="_blank" rel="noopener" class="sys-link card-inner px-4 py-3 rounded-lg group hover:border-indigo-500 transition-colors">
          <div class="flex items-center gap-3">
            <span class="w-2 h-2 rounded-full pulse-active inline-block"></span>
            <div>
              <div class="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors">ITGYANI</div>
              <div class="text-xs text-slate-500">itgyani.com</div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-emerald-400 font-medium">Online</span>
            <svg class="w-3.5 h-3.5 text-slate-600 group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
          </div>
        </a>
        <a href="https://kharadionline.com" target="_blank" rel="noopener" class="sys-link card-inner px-4 py-3 rounded-lg group hover:border-indigo-500 transition-colors">
          <div class="flex items-center gap-3">
            <span class="w-2 h-2 rounded-full pulse-active inline-block"></span>
            <div>
              <div class="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors">Kharadi Online</div>
              <div class="text-xs text-slate-500">kharadionline.com</div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-emerald-400 font-medium">Online</span>
            <svg class="w-3.5 h-3.5 text-slate-600 group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
          </div>
        </a>
      </div>
    </div>

    <!-- SECTION 3: MOM LOG -->
    <div class="card p-5 flex flex-col">
      <div class="flex items-center justify-between mb-4">
        <div>
          <p class="section-title">Section 03</p>
          <h2 class="text-lg font-bold text-white mt-0.5">MOM Log</h2>
        </div>
        <a href="/mom.json" target="_blank"
           class="text-xs bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg transition-colors font-medium flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          View JSON
        </a>
      </div>
      <div id="mom-content" class="flex-1">
        <div class="text-center py-12 text-slate-500">
          <svg class="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          <p class="text-sm font-medium">No meetings logged yet</p>
          <p class="text-xs mt-2 text-slate-