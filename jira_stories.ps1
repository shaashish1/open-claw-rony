$b64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("ashish@itgyani.com:JIRA_TOKEN_FROM_ENV"))
$headers = @{"Authorization"="Basic $b64"; "Accept"="application/json"; "Content-Type"="application/json"}
$base = "https://itgyani.atlassian.net"

$failedItems = @()
$createdStories = @()

function Make-Desc {
    param($agentText)
    return @{
        type = "doc"
        version = 1
        content = @(@{
            type = "paragraph"
            content = @(@{
                type = "text"
                text = $agentText
            })
        })
    }
}

function Create-Story {
    param($projectId, $issueTypeId, $summary, $priority, $labels, $descText, $epicKey)
    $fields = @{
        project = @{ id = $projectId }
        summary = $summary
        issuetype = @{ id = $issueTypeId }
        priority = @{ name = $priority }
        labels = $labels
        description = (Make-Desc $descText)
    }
    if ($epicKey) {
        $fields["parent"] = @{ key = $epicKey }
    }
    $body = @{ fields = $fields } | ConvertTo-Json -Depth 10
    try {
        $result = Invoke-RestMethod -Uri "$base/rest/api/3/issue" -Headers $headers -Method POST -Body $body
        Write-Host "  [OK] $($result.key) - $summary"
        $script:createdStories += "$($result.key): $summary"
        return $result.key
    } catch {
        $errMsg = $_.ToString()
        Write-Host "  [FAIL] $summary"
        $script:failedItems += "$summary"
        return $null
    }
}

# Epic keys from creation:
# IT-15 = ITGYANI Agency - First 5 Clients
# IT-16 = Email Infrastructure and 1M Leads Database
# IT-17 = Dashboard AI Models Panel
# IT-18 = AI Job Search and Apply App - MVP
# IT-19 = ITGYANI Agency - Scale to 20 Clients
# CG-52 = CryptoGyani.com SEO Launch
# CG-53 = CryptoGyani AdSense and Passive Income
# YUKTI-1 = OpenAlgo Audit and Trading Dashboard
# YUKTI-2 = Yukti Algo Trading SaaS Beta
# TEF-15 = OpenMAIC LMS Go-Live
# TEF-16 = TEF - First 100 Students Campaign
# KO-13 = Kharadi Online - ROAS 2x Campaign

# IT project storyType = 10012
# CG project storyType = 10001
# YUKTI project storyType = 10045
# TEF project storyType = 10008
# KO project storyType = 10001

Write-Host "=== STORIES: IT-15 ITGYANI Agency - First 5 Clients ==="
Create-Story "10006" "10012" "Build ITGYANI service menu and pricing page" "High" @("NIKKI","week1","revenue-engine1") "AGENT: NIKKI | WEEK: 1 | KRA: Create full service menu with pricing at itgyani.com | EST: 1d" "IT-15"
Create-Story "10006" "10012" "Cold email outreach to 100 prospects" "High" @("MAYA","week1","revenue-engine1") "AGENT: MAYA | WEEK: 1 | KRA: Send personalized cold emails to 100 qualified prospects | EST: 3d" "IT-15"
Create-Story "10006" "10012" "Create 3 automation demo packages" "High" @("VIKRAM","NIKKI","week1","revenue-engine1") "AGENT: VIKRAM+NIKKI | WEEK: 1 | KRA: Build 3 demo packages showcasing automation capabilities | EST: 2d" "IT-15"
Create-Story "10006" "10012" "LinkedIn outreach campaign - 50 DMs per day" "High" @("PRIYA","week1","revenue-engine1") "AGENT: PRIYA | WEEK: 1 | KRA: Run LinkedIn outreach at 50 DMs/day to target personas | EST: 5d" "IT-15"
Create-Story "10006" "10012" "Build sales proposal template" "High" @("KABIR","week1","revenue-engine1") "AGENT: KABIR | WEEK: 1 | KRA: Create professional sales proposal template for agency deals | EST: 1d" "IT-15"
Create-Story "10006" "10012" "Set up CRM pipeline in n8n" "High" @("ARJUN","NIKKI","week1","revenue-engine1") "AGENT: ARJUN+NIKKI | WEEK: 1 | KRA: Build n8n CRM pipeline to track leads and deals | EST: 2d" "IT-15"

Write-Host "=== STORIES: IT-16 Email Infrastructure and 1M Leads Database ==="
Create-Story "10006" "10012" "Audit and categorize all 8031 emails across 8 accounts" "High" @("MAYA","week1","email-infra") "AGENT: MAYA | WEEK: 1 | KRA: Full audit of all 8 email accounts, categorize by value | EST: 1d" "IT-16"
Create-Story "10006" "10012" "Build n8n email cleanup and auto-unsubscribe workflow" "High" @("ARJUN","week1","email-infra") "AGENT: ARJUN | WEEK: 1 | KRA: Automate email cleanup and unsubscribe management in n8n | EST: 1d" "IT-16"
Create-Story "10006" "10012" "Build lead scraper Phase 1 - 50K leads tech finance HR" "High" @("VEER","week1","email-infra") "AGENT: VEER | WEEK: 1 | KRA: Scrape 50K verified leads from tech/finance/HR sectors | EST: 5d" "IT-16"
Create-Story "10006" "10012" "Email validation and enrichment pipeline" "High" @("ARJUN","week1","email-infra") "AGENT: ARJUN | WEEK: 1 | KRA: Validate and enrich scraped leads with contact data | EST: 3d" "IT-16"
Create-Story "10006" "10012" "Set up SendGrid for bulk email delivery" "High" @("RAVI","week1","email-infra") "AGENT: RAVI | WEEK: 1 | KRA: Configure SendGrid account and warm-up for bulk sending | EST: 1d" "IT-16"
Create-Story "10006" "10012" "First email campaign - 50K sends" "High" @("MAYA","RAVI","week1","email-infra") "AGENT: MAYA+RAVI | WEEK: 1 | KRA: Execute first campaign to 50K leads, track opens and clicks | EST: 2d" "IT-16"

Write-Host "=== STORIES: IT-17 Dashboard AI Models Panel ==="
Create-Story "10006" "10012" "Add AI Models panel to dashboard.itgyani.com" "High" @("NIKKI","week1","dashboard") "AGENT: NIKKI | WEEK: 1 | KRA: Build AI models panel component for main dashboard | EST: 1d" "IT-17"
Create-Story "10006" "10012" "Show available models costs and status" "High" @("NIKKI","week1","dashboard") "AGENT: NIKKI | WEEK: 1 | KRA: Display all AI model status, costs per token, and availability | EST: 1d" "IT-17"
Create-Story "10006" "10012" "Add agent status and KPI tiles to dashboard" "High" @("NIKKI","week1","dashboard") "AGENT: NIKKI | WEEK: 1 | KRA: Agent status tiles showing active/idle/error state and KPIs | EST: 2d" "IT-17"
Create-Story "10006" "10012" "QA all dashboard panels - zero errors" "High" @("SARA","week1","dashboard") "AGENT: SARA | WEEK: 1 | KRA: Full QA pass on all dashboard panels, zero critical bugs | EST: 1d" "IT-17"
Create-Story "10006" "10012" "Performance test dashboard under load" "Medium" @("SARA","week1","dashboard") "AGENT: SARA | WEEK: 1 | KRA: Load test dashboard with realistic concurrent users | EST: 1d" "IT-17"

Write-Host "=== STORIES: IT-18 AI Job Search and Apply App MVP ==="
Create-Story "10006" "10012" "Validate demand - build landing page and collect 100 signups" "High" @("TARA","NIKKI","week2","jobapp") "AGENT: TARA+NIKKI | WEEK: 2 | KRA: Landing page live, 100 email signups validated | EST: 2d" "IT-18"
Create-Story "10006" "10012" "Build multi-portal job scraping engine" "High" @("ARJUN","week2","jobapp") "AGENT: ARJUN | WEEK: 2 | KRA: Scrape jobs from LinkedIn, Naukri, Indeed, Shine | EST: 3d" "IT-18"
Create-Story "10006" "10012" "Build AI resume tailor per job description" "High" @("ARJUN","NIKKI","week2","jobapp") "AGENT: ARJUN+NIKKI | WEEK: 2 | KRA: AI that rewrites resume to match each JD | EST: 3d" "IT-18"
Create-Story "10006" "10012" "Build auto-apply bot for LinkedIn Naukri Indeed" "High" @("ARJUN","week2","jobapp") "AGENT: ARJUN | WEEK: 2 | KRA: Automated application submission bot across major portals | EST: 4d" "IT-18"
Create-Story "10006" "10012" "Pricing Rs999 per month - payment integration" "High" @("RAVI","week2","jobapp") "AGENT: RAVI | WEEK: 2 | KRA: Razorpay integration at Rs999/mo subscription price | EST: 1d" "IT-18"
Create-Story "10006" "10012" "Beta launch - 10 paying users" "High" @("KABIR","week2","jobapp") "AGENT: KABIR | WEEK: 2 | KRA: Convert beta waitlist to 10 paying subscribers | EST: 2d" "IT-18"

Write-Host "=== STORIES: CG-52 CryptoGyani SEO Launch ==="
Create-Story "10002" "10001" "Final SEO audit and meta tags review" "High" @("PRIYA","week1","seo") "AGENT: PRIYA | WEEK: 1 | KRA: Complete SEO audit, all meta tags optimized | EST: 1d" "CG-52"
Create-Story "10002" "10001" "Set up Google Analytics 4 and Search Console" "High" @("ARJUN","week1","seo") "AGENT: ARJUN | WEEK: 1 | KRA: GA4 and GSC configured and tracking | EST: 0.5d" "CG-52"
Create-Story "10002" "10001" "Publish 10 SEO articles in crypto niche" "High" @("PRIYA","VEER","week1","seo") "AGENT: PRIYA+VEER | WEEK: 1 | KRA: 10 high-quality SEO articles published targeting crypto keywords | EST: 5d" "CG-52"
Create-Story "10002" "10001" "Launch announcement email to CryptoGyani list" "High" @("MAYA","week1","seo") "AGENT: MAYA | WEEK: 1 | KRA: Announcement email to full CryptoGyani subscriber list | EST: 1d" "CG-52"
Create-Story "10002" "10001" "Social media launch campaign" "High" @("PRIYA","week1","seo") "AGENT: PRIYA | WEEK: 1 | KRA: Multi-platform social launch campaign for CryptoGyani | EST: 2d" "CG-52"
Create-Story "10002" "10001" "Apply for Google AdSense" "High" @("RAVI","week1","seo") "AGENT: RAVI | WEEK: 1 | KRA: Submit AdSense application for CryptoGyani.com | EST: 0.5d" "CG-52"

Write-Host "=== STORIES: YUKTI-1 OpenAlgo Audit and Trading Dashboard ==="
Create-Story "10039" "10045" "Audit OpenAlgo current config on VPS" "High" @("ARJUN","week1","trading") "AGENT: ARJUN | WEEK: 1 | KRA: Full audit of OpenAlgo config at 194.233.64.74 | EST: 0.5d" "YUKTI-1"
Create-Story "10039" "10045" "Document current broker connections and strategies" "High" @("DISHA","week1","trading") "AGENT: DISHA | WEEK: 1 | KRA: Document all active broker APIs and running strategies | EST: 1d" "YUKTI-1"
Create-Story "10039" "10045" "Build Yukti trading dashboard UI" "High" @("NIKKI","week1","trading") "AGENT: NIKKI | WEEK: 1 | KRA: Full trading dashboard with P&L, positions, order book | EST: 3d" "YUKTI-1"
Create-Story "10039" "10045" "Integrate real-time P&L to ITGYANI dashboard" "Medium" @("NIKKI","DISHA","week1","trading") "AGENT: NIKKI+DISHA | WEEK: 1 | KRA: Live P&L feed into main ITGYANI dashboard | EST: 2d" "YUKTI-1"
Create-Story "10039" "10045" "Security audit of OpenAlgo endpoints" "High" @("ARJUN","week1","trading") "AGENT: ARJUN | WEEK: 1 | KRA: Security review of all OpenAlgo API endpoints | EST: 1d" "YUKTI-1"

Write-Host "=== STORIES: TEF-15 OpenMAIC LMS Go-Live ==="
Create-Story "10001" "10008" "Confirm deployment at learn.theemployeefactory.com" "High" @("TEF-AI","week1","lms") "AGENT: TEF-AI | WEEK: 1 | KRA: Verify LMS is live and accessible at learn.theemployeefactory.com | EST: 0.5d" "TEF-15"
Create-Story "10001" "10008" "Upload first 3 courses with pricing" "High" @("TEF-AI","week1","lms") "AGENT: TEF-AI | WEEK: 1 | KRA: 3 courses uploaded with descriptions, pricing, and preview | EST: 2d" "TEF-15"
Create-Story "10001" "10008" "Set up Razorpay and Stripe payment gateway" "High" @("RAVI","week1","lms") "AGENT: RAVI | WEEK: 1 | KRA: Razorpay + Stripe payment gateway live for course purchases | EST: 1d" "TEF-15"
Create-Story "10001" "10008" "QA test enroll and checkout flow" "High" @("SARA","week1","lms") "AGENT: SARA | WEEK: 1 | KRA: Full enroll and checkout flow tested, zero blockers | EST: 1d" "TEF-15"
Create-Story "10001" "10008" "Launch email to The Employee Factory list" "High" @("MAYA","week1","lms") "AGENT: MAYA | WEEK: 1 | KRA: Launch announcement email to TEF subscriber list | EST: 1d" "TEF-15"

Write-Host ""
Write-Host "=== STORY CREATION COMPLETE ==="
Write-Host "Total created: $($createdStories.Count)"
Write-Host "Total failed: $($failedItems.Count)"
if ($failedItems.Count -gt 0) {
    Write-Host "FAILED:"
    $failedItems | ForEach-Object { Write-Host "  - $_" }
}
