CREATE TABLE IF NOT EXISTS apx_prices (
  price_at         TIMESTAMP WITHOUT TIME ZONE NOT NULL PRIMARY KEY,
  tariff_usage     DOUBLE PRECISION NOT NULL,
  tariff_return    DOUBLE PRECISION NOT NULL
);

