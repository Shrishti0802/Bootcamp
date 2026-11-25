# Day 3 insights: vendor payments

1. **Top vendor:** Bluewave Logistics received the most money (78,847,890.60), about 6.8% of all paid amounts.
2. **Duplicates:** 500 invoices were paid twice, costing about 6,332,572.90. Fusion IT lost the most.
3. **Late payments:** 64.1% of paid invoices were late, by 10.5 days on average. Nova Software was worst, with 65.3% of its payments late.
4. **Overdue:** 8,076 invoices worth 100,848,995.16 are still unpaid and past their due date.
5. **Index:** looking up one invoice went from 5.269 ms (Seq Scan, read all 100,500 rows) to 0.068 ms (Index Scan), about 75x faster.