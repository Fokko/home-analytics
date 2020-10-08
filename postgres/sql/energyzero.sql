CREATE TABLE IF NOT EXISTS energy_usage (
  date_measured    TIMESTAMP WITHOUT TIME ZONE NOT NULL PRIMARY KEY,
  epex_price       DOUBLE PRECISION NOT NULL,
  energy_tax       DOUBLE PRECISION NOT NULL,
  trade_cost       DOUBLE PRECISION NOT NULL,
  ode_tax          DOUBLE PRECISION NOT NULL,
  network_cost     DOUBLE PRECISION NOT NULL,
  delivery_cost    DOUBLE PRECISION NOT NULL,
  deduction_tax    DOUBLE PRECISION NOT NULL,
  kwh_used         DOUBLE PRECISION NOT NULL,
  kwh_price        DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS solar_production (
  date_measured    TIMESTAMP WITHOUT TIME ZONE NOT NULL PRIMARY KEY,
  epex_price       DOUBLE PRECISION NOT NULL,
  energy_tax       DOUBLE PRECISION NOT NULL,
  trade_cost       DOUBLE PRECISION NOT NULL,
  ode_tax          DOUBLE PRECISION NOT NULL,
  kwh_used         DOUBLE PRECISION NOT NULL,
  kwh_price        DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS gas_usage (
  date_measured    TIMESTAMP WITHOUT TIME ZONE NOT NULL PRIMARY KEY,
  leba_price       DOUBLE PRECISION NOT NULL,
  energy_tax       DOUBLE PRECISION NOT NULL,
  trade_cost       DOUBLE PRECISION NOT NULL,
  network_cost     DOUBLE PRECISION NOT NULL,
  ode_tax          DOUBLE PRECISION NOT NULL,
  region_tax       DOUBLE PRECISION NOT NULL,
  delivery_cost    DOUBLE PRECISION NOT NULL,
  kwh_used         DOUBLE PRECISION NOT NULL,
  kwh_price        DOUBLE PRECISION NOT NULL
);
