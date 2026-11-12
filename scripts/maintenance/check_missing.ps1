$dir = 'D:\projects\supplier_crawler\classify_cache'
$expectedBatches = 237
$all = Get-ChildItem "$dir\batch_*.json" -ErrorAction SilentlyContinue
$mainCount = ($all | Where-Object { $_.Name -notmatch '_diff' }).Count

# Check which main batch numbers are missing
$existing = @{}
foreach ($f in $all) {
    if ($f.BaseName -match '^batch_(\d+)$') {
        $existing[[int]$Matches[1]] = $true
    }
}

$missing = @()
for ($i = 1; $i -le $expectedBatches; $i++) {
    if (-not $existing.ContainsKey($i)) { $missing += $i }
}

Write-Output "Main batches completed: $mainCount / $expectedBatches"
Write-Output "Missing batches ($($missing.Count)): $($missing -join ', ')"
