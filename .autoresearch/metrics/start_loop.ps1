# AutoResearch Loop: metrics/all-seven-functional
# Runs every 5 minutes until all 7 metrics are working
# To stop: Stop-Job -Name "ar-metrics-loop" ; Remove-Job -Name "ar-metrics-loop"

$env:PYTHONIOENCODING = "utf-8"
$scriptPath = Join-Path $PSScriptRoot "loop_runner.py"

Write-Host "Starting autoresearch loop: metrics/all-seven-functional"
Write-Host "Interval: 5 minutes"
Write-Host "To stop: Stop-Job -Name 'ar-metrics-loop'"

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] Running evaluation..."
    
    try {
        $result = & python $scriptPath 2>&1
        Write-Host $result
    } catch {
        Write-Host "[$timestamp] Error: $_"
    }
    
    # Check if goal achieved
    $resultsFile = Join-Path $PSScriptRoot "..\results.tsv"
    if (Test-Path $resultsFile) {
        $lastLine = (Get-Content $resultsFile | Select-Object -Last 1)
        if ($lastLine -match "KEEP" -and $lastLine -match "7") {
            Write-Host "`nGOAL ACHIEVED: All 7 metrics working!"
            break
        }
    }
    
    Write-Host "Next run in 5 minutes..."
    Start-Sleep -Seconds 300
}
