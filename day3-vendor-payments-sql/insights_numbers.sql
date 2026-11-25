WITH paid AS (SELECT * FROM payments WHERE paid_date IS NOT NULL),
top_v AS (SELECT vendor_name, SUM(amount) AS t FROM paid GROUP BY 1 ORDER BY t DESC LIMIT 1),
ranked AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY vendor_id, invoice_no ORDER BY payment_id) AS rn FROM payments),
dup_v AS (SELECT vendor_name, SUM(amount) AS a FROM ranked WHERE rn > 1 GROUP BY 1 ORDER BY a DESC LIMIT 1),
late_v AS (SELECT vendor_name, ROUND(100.0 * COUNT(*) FILTER (WHERE paid_date > due_date) / COUNT(*), 1) AS p FROM paid GROUP BY 1 ORDER BY p DESC LIMIT 1)
SELECT '1 top vendor' AS item,
       (SELECT vendor_name FROM top_v) || ' | ' || (SELECT t FROM top_v) || ' | '
       || ROUND(100.0 * (SELECT t FROM top_v) / (SELECT SUM(amount) FROM paid), 1) || '% of paid' AS result
UNION ALL
SELECT '2 duplicates',
       (SELECT COUNT(*) FROM ranked WHERE rn > 1) || ' invoices | ' || (SELECT SUM(amount) FROM ranked WHERE rn > 1)
       || ' total | worst vendor: ' || (SELECT vendor_name FROM dup_v)
UNION ALL
SELECT '3 late',
       ROUND(100.0 * COUNT(*) FILTER (WHERE paid_date > due_date) / COUNT(*), 1) || '% late | avg days late '
       || ROUND(AVG(paid_date - due_date) FILTER (WHERE paid_date > due_date), 1)
       || ' | worst vendor: ' || (SELECT vendor_name FROM late_v) || ' ' || (SELECT p FROM late_v) || '%'
FROM paid
UNION ALL
SELECT '4 overdue', COUNT(*) || ' invoices | ' || COALESCE(SUM(amount), 0)
FROM payments WHERE paid_date IS NULL AND due_date < CURRENT_DATE;