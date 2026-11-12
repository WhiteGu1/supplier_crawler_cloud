Get-WmiObject Win32_Process -Filter "ProcessId=11004 or ProcessId=12148" | Select-Object ProcessId, CommandLine | Format-List
