# Check for the batch processing script and find total
$batchScripts = Get-ChildItem 'D:\projects\supplier_crawler\' -Filter '*batch*' -Recurse -ErrorAction SilentlyContinue
foreach ($f in $batchScripts) {
    Write-Host "$($f.FullName) | $([math]::Round($f.Length/1KB,1))KB"
}

# Also check for any running python process command lines
Get-WmiObject Win32_Process -Filter "Name='python.exe'" | Select-Object ProcessId, CommandLine | Format-List
