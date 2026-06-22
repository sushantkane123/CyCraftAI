# ============================================================================
# BradlyAI L1 Agent - Quick Test Script (Windows PowerShell)
# Usage:  .\test-l1.ps1
# ============================================================================

$base = "http://localhost:8000"

Write-Host "`n=== 1. L1 Agent status ===" -ForegroundColor Cyan
$mode = Invoke-RestMethod -Uri "$base/api/v1/l1/mode" -Method Get
Write-Host "  Mode: $($mode.mode) | Threshold: $($mode.threshold)"

Write-Host "`n=== 2. Nessus scan (should CLOSE) ===" -ForegroundColor Cyan
$body = @{
    source = "splunk"
    payload = @{
        search_name = "Nessus vulnerability scan completed"
        result = @{ host = "srv" }
        severity = "high"
    }
} | ConvertTo-Json -Depth 5
$resp = Invoke-RestMethod -Uri "$base/api/v1/l1/process-alert" -Method Post -ContentType "application/json" -Body $body
Write-Host "  Decision:    $($resp.decision) ($([math]::Round($resp.confidence * 100))%)"
Write-Host "  Reason:      $($resp.reason.Substring(0, [Math]::Min(100, $resp.reason.Length)))"
Write-Host "  Closed:      $($resp.applied.alert_closed)"
Write-Host "  Primary:     $($resp.primary_signal)"

Write-Host "`n=== 3. Wazuh PowerShell threat (should ESCALATE) ===" -ForegroundColor Cyan
$body = @{
    source = "wazuh"
    payload = @{
        rule  = @{ level = 12; description = "Suspicious PowerShell execution detected"; id = "100001" }
        agent = @{ name = "WEB-SRV01"; ip = "10.0.0.50" }
    }
} | ConvertTo-Json -Depth 5
$resp = Invoke-RestMethod -Uri "$base/api/v1/l1/process-alert" -Method Post -ContentType "application/json" -Body $body
Write-Host "  Decision:    $($resp.decision) ($([math]::Round($resp.confidence * 100))%)"

Write-Host "`n=== 4. Batch (3 alerts: 2 benign + 1 real) ===" -ForegroundColor Cyan
$batch = @{
    alerts = @(
        @{
            source = "splunk"
            payload = @{
                search_name = "Prometheus monitor alert fired"
                result = @{ src_ip = "10.0.0.100" }
                severity = "low"
            }
        },
        @{
            source = "wazuh"
            payload = @{
                rule  = @{ level = 12; description = "lsass memory dump attempt"; id = "100002" }
                agent = @{ name = "DEV-WIN-SRV09"; ip = "10.0.0.5" }
            }
        },
        @{
            source = "splunk"
            payload = @{
                search_name = "GET /health probe"
                result = @{ src_ip = "127.0.0.1" }
                severity = "low"
            }
        }
    )
} | ConvertTo-Json -Depth 8
$resp = Invoke-RestMethod -Uri "$base/api/v1/l1/process-batch" -Method Post -ContentType "application/json" -Body $batch
Write-Host "  Total: $($resp.total) | Closed: $($resp.closed) | Escalated: $($resp.escalated) | Errors: $($resp.errors)"
foreach ($r in $resp.results) {
    if ($r.decision) {
        Write-Host "    $($r.alert_id.PadRight(20)) $($r.decision.PadRight(15)) $($r.confidence)"
    }
}

Write-Host "`n=== 5. Stats ===" -ForegroundColor Cyan
$stats = Invoke-RestMethod -Uri "$base/api/v1/l1/stats?since_hours=1" -Method Get
Write-Host "  Total decisions:  $($stats.total_decisions)"
Write-Host "  Closed:           $($stats.closed)"
Write-Host "  Escalated:        $($stats.escalated)"
Write-Host "  Auto-close rate:  $([math]::Round($stats.auto_close_rate * 100))%"
Write-Host "  Override rate:    $([math]::Round($stats.override_rate * 100))%"

Write-Host "`n=== 6. Whitelist ===" -ForegroundColor Cyan
$wl = Invoke-RestMethod -Uri "$base/api/v1/l1/whitelist" -Method Get
Write-Host "  Entries: $($wl.count)"
foreach ($e in $wl.entries) {
    Write-Host "    #$($e.id) $($e.entry_type.PadRight(12)) = $($e.match_value.PadRight(30)) ($($e.name))"
}

Write-Host "`n=== 7. Recent audit log ===" -ForegroundColor Cyan
$audit = Invoke-RestMethod -Uri "$base/api/v1/l1/audit?since_hours=1&limit=5" -Method Get
Write-Host "  Total decisions in last hour: $($audit.count)"
foreach ($e in $audit.entries) {
    Write-Host "    #$($e.id) [$($e.decision.PadRight(14))] $($e.alert_id.PadRight(18)) $([math]::Round($e.confidence * 100))% signal=$($e.primary_signal)"
}

Write-Host "`n=== 8. Switch to SHADOW mode (safe) ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "$base/api/v1/l1/mode" -Method Post -ContentType "application/json" -Body '{"mode":"shadow"}'
Write-Host "  ✅ Now in SHADOW mode - decisions logged but no auto-close" -ForegroundColor Yellow

Write-Host "`n=== 9. Switch back to ACTIVE mode ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "$base/api/v1/l1/mode" -Method Post -ContentType "application/json" -Body '{"mode":"active"}'
Write-Host "  ✅ Now in ACTIVE mode - auto-close enabled" -ForegroundColor Green

Write-Host "`nL1 Agent test complete." -ForegroundColor Green
