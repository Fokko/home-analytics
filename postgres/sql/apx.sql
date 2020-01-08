SET timezone = 'Europe/Amsterdam';


CREATE TABLE IF NOT EXISTS apx_prices (
  price_at         TIMESTAMP NOT NULL PRIMARY KEY,
  price_raw_ex_vat DOUBLE PRECISION NOT NULL
);
