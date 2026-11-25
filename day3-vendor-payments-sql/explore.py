import pandas as pd

df = pd.read_csv("data/payments.csv", parse_dates=["invoice_date", "due_date", "paid_date"])

print("Shape (rows, cols):", df.shape)
print("\nColumn types:\n", df.dtypes)
print("\nMissing values per column:\n", df.isna().sum())
print("\nFirst rows:\n", df.head())
print("\nAmount summary:\n", df["amount"].describe())
print("\nRepeated vendor+invoice pairs:", df.duplicated(subset=["vendor_id", "invoice_no"]).sum())