CREATE TABLE IF NOT EXISTS youless_readings (
  created_at       TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  net_counter      DOUBLE PRECISION NOT NULL,
  power            DOUBLE PRECISION NOT NULL,
  consumption_high DOUBLE PRECISION NOT NULL,
  consumption_low  DOUBLE PRECISION NOT NULL,
  production_high  DOUBLE PRECISION NOT NULL,
  production_low   DOUBLE PRECISION NOT NULL,
  gas              DOUBLE PRECISION NOT NULL
);
