import subprocess
import re

cmd = [
    r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqlbinlog.exe",
    "-v",
    "--base64-output=DECODE-ROWS",
    "--start-datetime=2026-10-14 12:00:00",
    "--database=supplier_crawler",
    r"C:\ProgramData\MySQL\MySQL Server 8.0\Data\SERVER-bin.000108"
]

print("Running mysqlbinlog...")
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")

delete_events = []
current_delete = []
in_delete = False
table_name = ""

for line in proc.stdout:
    if "DELETE FROM" in line or "### DELETE FROM" in line:
        in_delete = True
        current_delete = [line]
    elif in_delete:
        if line.startswith("###") or line.startswith("#"):
            current_delete.append(line)
        else:
            in_delete = False
            full_block = "".join(current_delete)
            if "cart_items" in full_block:
                delete_events.append(full_block)
            current_delete = []

if current_delete and "cart_items" in "".join(current_delete):
    delete_events.append("".join(current_delete))

proc.wait()
print(f"Found {len(delete_events)} DELETE blocks on cart_items.")
if delete_events:
    print("Sample last delete block:")
    print(delete_events[-1][:1000])

    with open("recovered_deletes.txt", "w", encoding="utf-8") as f:
        f.write("\n=== EVENT ===\n".join(delete_events))
    print("Wrote recovered_deletes.txt")
