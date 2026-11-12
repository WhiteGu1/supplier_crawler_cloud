$files = Get-ChildItem 'D:\projects\supplier_crawler\classify_cache\batch_*.json'
$normal = $files | Where-Object { $_.Name -notmatch '_diff' } | Sort-Object { [int]($_.BaseName -replace 'batch_', '') }
$lastNormal = $normal | Select-Object -Last 1
$firstNormal = $normal | Select-Object -First 1
Write-Output "First normal batch: $($firstNormal.Name)"
Write-Output "Last normal batch: $($lastNormal.Name)"
Write-Output "Normal batch count: $($normal.Count)"
# Check for gaps
$numbers = $normal | ForEach-Object { [int]($_.BaseName -replace 'batch_', '') }
$maxNum = ($numbers | Measure-Object -Maximum).Maximum
$minNum = ($numbers | Measure-Object -Minimum).Minimum
Write-Output "Min batch number: $minNum"
Write-Output "Max batch number: $maxNum"
Write-Output "Expected count if no gaps: $($maxNum - $minNum + 1)"
$lastWrite = $lastNormal.LastWriteTime
Write-Output "Last batch write time: $lastWrite"
$now = Get-Date
$elapsed = ($now - $lastWrite).TotalHours
Write-Output "Hours since last batch: $([math]::Round($elapsed, 1))h"
