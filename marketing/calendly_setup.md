# Cal.com Booking Page Setup â€” ITGYANI

**Status check (2026-04-26):**
- `cal.com/itgyani` â†’ âŒ 404 â€” account does NOT exist yet
- `cal.com/ashish-itgyani` â†’ âŒ 404 â€” account does NOT exist yet

Both slugs are available. Target URL: **https://cal.com/itgyani/15min**

---

## Manual Setup Steps

### Step 1: Create Account
1. Go to https://app.cal.com/signup
2. Sign up with:
   - Email: `ashish@itgyani.com`
   - Name: `Ashish Sharma â€” ITGYANI`
3. Verify email

### Step 2: Set Username (Critical!)
1. After signup, go to **Settings â†’ Profile**
2. Set username to: **`itgyani`**
   - This gives you: `https://cal.com/itgyani`
   - âš ï¸ Do this FIRST before creating events â€” username cannot be changed easily later

### Step 3: Create the Event Type
1. Go to **Event Types â†’ + New Event Type**
2. Fill in:
   - **Title:** `Free 15-min AI Automation Call`
   - **URL slug:** `demo`
   - **Duration:** `15 minutes`
   - **Description:**
     ```
     Book a free 15-minute call to see how AI agents can automate your business. ITGYANI builds AI employees that work 24x7.
     ```
3. Click **Continue**

### Step 4: Connect Calendar
1. Go to **Settings â†’ Calendars**
2. Connect your Google Calendar (ashish@itgyani.com)
3. Set availability hours (suggest: Monâ€“Fri, 10amâ€“7pm IST)

### Step 5: Configure Event Settings
1. Back in the event type, set:
   - **Location:** Google Meet (auto-generate link)
   - **Buffer time:** 5 min after
   - **Min notice:** 1 hour
2. Save

### Step 6: Test & Share
1. Open: https://cal.com/itgyani/15min
2. Book a test slot (use a personal email)
3. Confirm calendar invite arrives at ashish@itgyani.com

---

## Final Booking URL
```
https://cal.com/itgyani/15min
```

## Embed Code (for landing page)
```html
<!-- Cal.com inline embed -->
<div style="width:100%;height:700px;overflow:hidden">
  <iframe 
    src="https://cal.com/itgyani/15min?embed=true" 
    style="width:100%;height:100%;border:0"
    frameborder="0"
  ></iframe>
</div>
```

## Alternative: Popup Embed
```html
<!-- Add to <head> -->
<script type="text/javascript">
(function (C, A, L) { let p = function (a, ar) { a.q.push(ar); }; let d = C.document; C.Cal = C.Cal || function () { let cal = C.Cal; let ar = arguments; if (!cal.loaded) { cal.ns = {}; cal.q = cal.q || []; d.head.appendChild(d.createElement("script")).src = A; cal.loaded = true; } if (ar[0] === L) { const api = function () { p(api, arguments); }; const namespace = ar[1]; api.q = api.q || []; typeof namespace === "string" ? (cal.ns[namespace] = api) && p(api, ar) : p(cal, ar); return; } p(cal, ar); }; })(window, "https://app.cal.com/embed/embed.js", "init");
Cal("init", {origin:"https://cal.com"});
</script>

<!-- Button trigger -->
<button data-cal-link="itgyani/demo" data-cal-config='{"layout":"month_view"}'>
  ðŸ“… Book Free Call
</button>
```

---

## Notes
- Cal.com free plan supports unlimited 1:1 bookings
- No credit card needed for basic use
- Team features require paid plan
- Alternative slug if `itgyani` is taken: `ashish-itgyani` or `itgyani-ashish`

