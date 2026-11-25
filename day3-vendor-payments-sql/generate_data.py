import csv
import os
import random
from datetime import date, timedelta

random.seed(42)  # same seed = same data every time

VENDORS = [(f"V{i:03d}", name) for i, name in enumerate(
    ["Acme Supplies", "Bluewave Logistics", "Cedar Tools", "Delta Packaging",
     "Evergreen Foods", "Fusion IT", "Granite Works", "Horizon Print",
     "Indus Cleaning", "Jade Electricals", "Keystone Steel", "Lotus Stationery",
     "Metro Transport", "Nova Software", "Orbit Security"], start=1)]
METHODS = ["BANK_TRANSFER", "CARD", "CHEQUE", None]  # None = missing value

N_INVOICES = 100_000
rows = []
pid = 1

for i in range(1, N_INVOICES + 1):
    vendor_id, vendor_name = random.choice(VENDORS)
    invoice_date = date(2025, 1, 1) + timedelta(days=random.randint(0, 330))
    due_date = invoice_date + timedelta(days=30)
    amount = round(random.uniform(200, 25000), 2)
    if random.random() < 0.08:
        paid_date, status = None, "UNPAID"
    else:
        paid_date = due_date + timedelta(days=random.randint(-10, 20))
        status = "PAID"
    rows.append([pid, f"INV-{i:06d}", vendor_id, vendor_name, invoice_date,
                 due_date, paid_date, amount, random.choice(METHODS), status])
    pid += 1

# Plant duplicates: the same invoice paid a second time a few days later
paid_rows = [r for r in rows if r[9] == "PAID"]
for r in random.sample(paid_rows, 500):
    dup = r.copy()
    dup[0] = pid
    dup[6] = r[6] + timedelta(days=random.randint(1, 5))
    rows.append(dup)
    pid += 1

os.makedirs("data", exist_ok=True)
with open("data/payments.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["payment_id", "invoice_no", "vendor_id", "vendor_name",
                "invoice_date", "due_date", "paid_date", "amount",
                "payment_method", "status"])
    w.writerows(rows)

print(f"Wrote {len(rows)} rows to data/payments.csv")