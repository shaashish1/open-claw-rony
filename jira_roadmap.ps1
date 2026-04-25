$b64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("ashish@itgyani.com:JIRA_TOKEN_FROM_ENV"))
$headers = @{"Authorization"="Basic $b64"; "Accept"="application/json"; "Content-Type"="application/json"}
$base = "https://itgyani.atlassian.net"

$epicResults = @{}
$failedItems = @()

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

function Create-Issue {
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
        return $result.key
    } catch {
        $errMsg = $_.ToString()
        Write-Host "  [FAIL] $summary :: $errMsg"
        $script:failedItems += "$summary :: $errMsg"
        return $null
    }
}

Write-Host "=== CREATING IT EPICS ==="

$name1 = "ITGYANI Agency - First 5 Clients"
$e1 = Create-Issue "10006" "10013" $name1 "High" @("KABIR","MAYA","week1") "AGENT: KABIR+MAYA | WEEK: 1 | KRA: Sign first 5 agency clients" $null
$epicResults["IT_AGENCY_5"] = $e1

$name2 = "Email Infrastructure and 1M Leads Database"
$e2 = Create-Issue "10006" "10013" $name2 "High" @("MAYA","ARJUN","week1") "AGENT: MAYA+ARJUN | WEEK: 1 | KRA: Build 1M leads database and email delivery" $null
$epicResults["IT_EMAIL"] = $e2

$name3 = "Dashboard AI Models Panel"
$e3 = Create-Issue "10006" "10013" $name3 "High" @("NIKKI","SARA","week1") "AGENT: NIKKI+SARA | WEEK: 1 | KRA: AI models panel on dashboard.itgyani.com" $null
$epicResults["IT_DASHBOARD"] = $e3

$name4 = "AI Job Search and Apply App - MVP"
$e4 = Create-Issue "10006" "10013" $name4 "High" @("ARJUN","NIKKI","TARA","week2") "AGENT: ARJUN+NIKKI+TARA | WEEK: 2 | KRA: MVP of AI job search auto-apply platform" $null
$epicResults["IT_JOBAPP"] = $e4

$name5 = "ITGYANI Agency - Scale to 20 Clients"
$e5 = Create-Issue "10006" "10013" $name5 "Medium" @("KABIR","MAYA","week3") "AGENT: KABIR+MAYA | WEEK: 3 | KRA: Scale agency from 5 to 20 clients" $null
$epicResults["IT_AGENCY_20"] = $e5

Write-Host "=== CREATING CG EPICS ==="

$name6 = "CryptoGyani.com SEO Launch"
$e6 = Create-Issue "10002" "10000" $name6 "High" @("PRIYA","NIKKI","MAYA","week1") "AGENT: PRIYA+NIKKI+MAYA | WEEK: 1 | KRA: Launch CryptoGyani.com with full SEO" $null
$epicResults["CG_SEO"] = $e6

$name7 = "CryptoGyani AdSense and Passive Income"
$e7 = Create-Issue "10002" "10000" $name7 "Medium" @("PRIYA","VEER","week2") "AGENT: PRIYA+VEER | WEEK: 2 | KRA: AdSense and passive income for CryptoGyani" $null
$epicResults["CG_ADSENSE"] = $e7

Write-Host "=== CREATING YUKTI EPICS ==="

$name8 = "OpenAlgo Audit and Trading Dashboard"
$e8 = Create-Issue "10039" "10046" $name8 "High" @("ARJUN","NIKKI","DISHA","week1") "AGENT: ARJUN+NIKKI+DISHA | WEEK: 1 | KRA: Audit OpenAlgo and build trading dashboard" $null
$epicResults["YUKTI_OPENALGO"] = $e8

$name9 = "Yukti Algo Trading SaaS Beta"
$e9 = Create-Issue "10039" "10046" $name9 "Medium" @("DISHA","VIKRAM","week3") "AGENT: DISHA+VIKRAM | WEEK: 3 | KRA: Launch Yukti algo trading SaaS beta" $null
$epicResults["YUKTI_SAAS"] = $e9

Write-Host "=== CREATING TEF EPICS ==="

$name10 = "OpenMAIC LMS Go-Live"
$e10 = Create-Issue "10001" "10006" $name10 "High" @("TEF-AI","NIKKI","week1") "AGENT: TEF-AI+NIKKI | WEEK: 1 | KRA: Deploy OpenMAIC LMS at learn.theemployeefactory.com" $null
$epicResults["TEF_LMS"] = $e10

$name11 = "TEF - First 100 Students Campaign"
$e11 = Create-Issue "10001" "10006" $name11 "Medium" @("MAYA","PRIYA","week2") "AGENT: MAYA+PRIYA | WEEK: 2 | KRA: Enroll first 100 paying students" $null
$epicResults["TEF_STUDENTS"] = $e11

Write-Host "=== CREATING KO EPICS ==="

$name12 = "Kharadi Online - ROAS 2x Campaign"
$e12 = Create-Issue "10003" "10000" $name12 "Medium" @("KIRAN","PRIYA","week3") "AGENT: KIRAN+PRIYA | WEEK: 3 | KRA: Double ROAS on Kharadi Online ad campaigns" $null
$epicResults["KO_ROAS"] = $e12

Write-Host ""
Write-Host "=== EPIC CREATION COMPLETE ==="
foreach ($key in $epicResults.Keys) {
    Write-Host "  $key => $($epicResults[$key])"
}
