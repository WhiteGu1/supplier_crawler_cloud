# Check the newest batch files to understand state
$files = Get-ChildItem 'D:\projects\supplier_crawler\classify_cache\batch_*.json' | Sort-Object Name -Descending | Select-Object -First 10
$files | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize

# Also check if there's a log file
Get-ChildItem 'D:\projects\supplier_crawler\*.log' -ErrorAction SilentlyContinue | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize

# Check for any error/log output directories
Get-ChildItem 'D:\projects\supplier_crawler\' -Directory | Select-Object Name | Format-Table -AutoSize
