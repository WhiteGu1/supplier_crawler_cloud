$files = Get-ChildItem 'D:\projects\supplier_crawler\classify_cache\batch_*.json' -File | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name, LastWriteTime, @{N='SizeKB';E={[math]::Round($_.Length/1KB,1)}}
$files | Format-Table -AutoSize
Write-Host "---"
$latest = Get-ChildItem 'D:\projects\supplier_crawler\classify_cache\batch_*.json' -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Write-Host "Latest file: $($latest.Name) at $($latest.LastWriteTime)"
$now = Get-Date
$diff = $now - $latest.LastWriteTime
Write-Host "Time since last file: $([math]::Round($diff.TotalMinutes,1)) minutes ago"
