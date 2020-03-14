CREATE TABLE IF NOT EXISTS tesla_readings (
  created_at             TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
  battery_level          DOUBLE PRECISION NOT NULL,
  charger_actual_current DOUBLE PRECISION NOT NULL,
  charger_power          DOUBLE PRECISION NOT NULL,
  charger_voltage        DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS tesla_charge_schema (
  created_at             TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  slot_start             TIMESTAMP WITHOUT TIME ZONE NOT NULL,
  price_kwh              DOUBLE PRECISION NOT NULL,
  est_charge             DOUBLE PRECISION NOT NULL,
  PRIMARY KEY(created_at, slot_start)
);


