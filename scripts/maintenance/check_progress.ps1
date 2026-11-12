$files = Get-ChildItem 'D:\projects\supplier_crawler\classify_cache\batch_*.json' -ErrorAction SilentlyContinue
$total = $files.Count
$maxBatch = 0
foreach ($f in $files) {
    if ($f.Name -match 'batch_(\d+)') {
        $n = [int]$Matches[1]
        if ($n -gt $maxBatch) {
            $maxBatch = $n
        }
    }
}
$diffCount = ($files | Where-Object { $_.Name -match '_diff\.json$' }).Count
$normalCount = $total - $diffCount
Write-Output "Total files: $total"
Write-Output "Normal batches: $normalCount"
Write-Output "Diff batches: $diffCount"
Write-Output "Max batch number: $maxBatch"
$pct = [math]::Round($maxBatch / 23601 * 100, 2)
Write-Output "Progress: $maxBatch / 23601 = $pct%"
