$procs = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'classif' }
if ($procs) {
    foreach ($p in $procs) {
        Write-Output "PID: $($p.ProcessId)"
        Write-Output "CMD: $($p.CommandLine)"
    }
} else {
    Write-Output "No classify-related process running."
}
