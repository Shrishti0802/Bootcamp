import pandas as pd
import psycopg

CONN = "postgresql://postgres:postgres@localhost:5433/vendors"

df = pd.read_csv("data/payments.csv")
df = df.astype(object).where(df.notna(), None)  # turn NaN into real NULLs

with psycopg.connect(CONN) as conn:
    with conn.cursor() as cur:
        cur.execute(open("schema.sql").read())
        with cur.copy("COPY payments FROM STDIN") as copy:
            for row in df.itertuples(index=False):
                copy.write_row(row)
        cur.execute("SELECT COUNT(*) FROM payments")
        print("Rows in table:", cur.fetchone()[0])