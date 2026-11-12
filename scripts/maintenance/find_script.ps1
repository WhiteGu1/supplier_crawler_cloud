# Check the classify script to understand total batches
$classifyScript = Get-ChildItem 'D:\projects\supplier_crawler\' -Filter 'classify*.py' -Recurse | Select-Object -First 5
foreach ($f in $classifyScript) {
    Write-Host "Found: $($f.FullName)"
}

# Also check for any config or log that mentions total
$logFiles = Get-ChildItem 'D:\projects\supplier_crawler\' -Filter '*.log' -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3
foreach ($f in $logFiles) {
    Write-Host "Log: $($f.FullName) | $($f.LastWriteTime) | $([math]::Round($f.Length/1KB,1))KB"
}
