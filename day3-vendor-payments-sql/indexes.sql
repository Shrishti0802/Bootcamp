-- BEFORE the index: look up one invoice
EXPLAIN ANALYZE SELECT * FROM payments WHERE invoice_no = 'INV-050000';

CREATE INDEX idx_payments_invoice_no ON payments (invoice_no);
ANALYZE payments;

-- AFTER the index: same lookup
EXPLAIN ANALYZE SELECT * FROM payments WHERE invoice_no = 'INV-050000';