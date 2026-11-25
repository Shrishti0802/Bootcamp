DROP TABLE IF EXISTS payments;

CREATE TABLE payments (
    payment_id     INT PRIMARY KEY,
    invoice_no     TEXT NOT NULL,
    vendor_id      TEXT NOT NULL,
    vendor_name    TEXT NOT NULL,
    invoice_date   DATE NOT NULL,
    due_date       DATE NOT NULL,
    paid_date      DATE,
    amount         NUMERIC(12,2) NOT NULL,
    payment_method TEXT,
    status         TEXT NOT NULL
);