SET timezone = 'Europe/Amsterdam';

CREATE TABLE IF NOT EXISTS tesla_readings (
  created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
  battery_level          DOUBLE PRECISION NOT NULL,
  charger_actual_current DOUBLE PRECISION NOT NULL,
  charger_power          DOUBLE PRECISION NOT NULL,
  charger_voltage        DOUBLE PRECISION NOT NULL
);
