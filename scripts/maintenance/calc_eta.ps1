$files = Get-ChildItem 'D:\projects\supplier_crawler\classify_cache\' -Filter 'batch_*.json'
$pureBatches = $files | Where-Object { $_.Name -match '^batch_\d+\.json$' }
$pureCount = $pureBatches.Count

$total = 23601
$batchesNeeded = [math]::Ceiling($total / 100)
$progress = [math]::Round(($pureCount / $batchesNeeded) * 100, 1)

# Get first and last batch times to calculate rate
$sorted = $pureBatches | Sort-Object LastWriteTime
$first = $sorted | Select-Object -First 1
$latest = $sorted | Select-Object -Last 1

$timeSpan = $latest.LastWriteTime - $first.LastWriteTime
$totalMinutes = $timeSpan.TotalMinutes

if ($totalMinutes -gt 0) {
    $ratePerMin = [math]::Round($pureCount / $totalMinutes, 2)
    $remaining = $batchesNeeded - $pureCount
    $etaMinutes = [math]::Round($remaining / $ratePerMin, 0)
    $etaHours = [math]::Round($etaMinutes / 60, 1)
    
    Write-Output "PROGRESS_PERCENT=$progress"
    Write-Output "DONE=$pureCount"
    Write-Output "TOTAL=$batchesNeeded"
    Write-Output "RATE=$ratePerMin batches/min"
    Write-Output "REMAINING=$remaining batches"
    Write-Output "ETA_MINUTES=$etaMinutes"
    Write-Output "ETA_HOURS=$etaHours"
    Write-Output "FIRST_BATCH_TIME=$($first.LastWriteTime)"
    Write-Output "LATEST_BATCH_TIME=$($latest.LastWriteTime)"
    Write-Output "ELAPSED_MIN=$([math]::Round($totalMinutes,1))"
} else {
    Write-Output "PROGRESS_PERCENT=$progress"
    Write-Output "DONE=$pureCount"
    Write-Output "TOTAL=$batchesNeeded"
}
