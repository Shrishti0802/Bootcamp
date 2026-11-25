-- 1. Top 10 vendors by total amount paid (note: includes duplicate payments)
SELECT vendor_name, SUM(amount) AS total_paid, COUNT(*) AS payments
FROM payments
WHERE paid_date IS NOT NULL
GROUP BY vendor_name
ORDER BY total_paid DESC
LIMIT 10;

-- 2. Duplicate payments: same vendor + invoice paid more than once.
-- ROW_NUMBER numbers each copy; rn > 1 are the extra payments.
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY vendor_id, invoice_no ORDER BY payment_id) AS rn
    FROM payments
) t
WHERE rn > 1
ORDER BY amount DESC;

-- 3. Monthly totals paid
SELECT DATE_TRUNC('month', paid_date)::date AS month,
       SUM(amount) AS total_paid,
       COUNT(*) AS payments
FROM payments
WHERE paid_date IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- 4. Late payments: how many, and average days late
SELECT COUNT(*) AS late_payments,
       ROUND(AVG(paid_date - due_date), 1) AS avg_days_late
FROM payments
WHERE paid_date > due_date;

-- 5. Vendors with the highest late-payment percentage.
-- HAVING filters groups (vendors) after counting; WHERE could not do this.
SELECT vendor_name,
       COUNT(*) AS payments,
       ROUND(100.0 * COUNT(*) FILTER (WHERE paid_date > due_date) / COUNT(*), 1) AS late_pct
FROM payments
WHERE paid_date IS NOT NULL
GROUP BY vendor_name
HAVING COUNT(*) >= 100
ORDER BY late_pct DESC;

-- 6. Unpaid invoices already past their due date, by vendor
SELECT vendor_name, COUNT(*) AS overdue_invoices, SUM(amount) AS overdue_amount
FROM payments
WHERE paid_date IS NULL AND due_date < CURRENT_DATE
GROUP BY vendor_name
ORDER BY overdue_amount DESC;

-- 7. Payments and average amount by payment method (missing method shown as UNKNOWN)
SELECT COALESCE(payment_method, 'UNKNOWN') AS method,
       COUNT(*) AS payments,
       ROUND(AVG(amount), 2) AS avg_amount
FROM payments
GROUP BY 1
ORDER BY payments DESC;

-- 8. The 5 largest single payments
SELECT payment_id, invoice_no, vendor_name, amount, paid_date
FROM payments
WHERE paid_date IS NOT NULL
ORDER BY amount DESC
LIMIT 5;

-- 9. Month-over-month change in total paid (LAG looks at the previous row)
WITH monthly AS (
    SELECT DATE_TRUNC('month', paid_date)::date AS month, SUM(amount) AS total
    FROM payments
    WHERE paid_date IS NOT NULL
    GROUP BY 1
)
SELECT month, total,
       total - LAG(total) OVER (ORDER BY month) AS change_vs_prev_month
FROM monthly
ORDER BY month;

-- 10. Money lost to duplicate payments, by vendor
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY vendor_id, invoice_no ORDER BY payment_id) AS rn
    FROM payments
)
SELECT vendor_name, COUNT(*) AS duplicate_payments, SUM(amount) AS duplicated_amount
FROM ranked
WHERE rn > 1
GROUP BY vendor_name
ORDER BY duplicated_amount DESC;