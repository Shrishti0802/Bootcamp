import csv
import sys
import time

from triage import triage

version = sys.argv[1] if len(sys.argv) > 1 else "v1"
rows = list(csv.DictReader(open("samples.csv", encoding="utf-8")))
out, correct = [], 0

for r in rows:
    res = triage(r["complaint"], version)
    time.sleep(2)  # be gentle with free-tier rate limits
    got_eq = res.equipment.lower().strip() if res else ""
    got_ur = res.urgency if res else ""
    got_ho = (res.hospital or "").strip().lower() if res else ""
    ok = (
        res is not None
        and got_eq == r["equipment"].lower()
        and got_ur == r["urgency"]
        and got_ho == r["hospital"].lower()
    )
    correct += ok
    out.append({
        "id": r["id"], "expected_equipment": r["equipment"], "got_equipment": got_eq,
        "expected_urgency": r["urgency"], "got_urgency": got_ur,
        "expected_hospital": r["hospital"], "got_hospital": got_ho,
        "got_next_action": res.next_action if res else "", "correct": int(ok),
    })

pct = round(100 * correct / len(rows))
with open(f"accuracy_{version}.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=out[0].keys())
    w.writeheader()
    w.writerows(out)
    f.write(f"OVERALL,{correct}/{len(rows)},{pct}%\n")

print(f"{version}: {correct}/{len(rows)} correct = {pct}%")