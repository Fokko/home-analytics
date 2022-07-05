CREATE TABLE IF NOT EXISTS youless_readings (
  created_at       TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
  net_counter      DOUBLE PRECISION NOT NULL,
  power            DOUBLE PRECISION NOT NULL,
  consumption_high DOUBLE PRECISION NOT NULL,
  consumption_low  DOUBLE PRECISION NOT NULL,
  production_high  DOUBLE PRECISION NOT NULL,
  production_low   DOUBLE PRECISION NOT NULL,

  tarrif           SMALLINT NOT NULL,

  current_phase_1  DOUBLE PRECISION NOT NULL,
  current_phase_2  DOUBLE PRECISION NOT NULL,
  current_phase_3  DOUBLE PRECISION NOT NULL,

  voltage_phase_1  DOUBLE PRECISION NOT NULL,
  voltage_phase_2  DOUBLE PRECISION NOT NULL,
  voltage_phase_3  DOUBLE PRECISION NOT NULL,

  load_phase_1     INTEGER NOT NULL,
  load_phase_2     INTEGER NOT NULL,
  load_phase_3     INTEGER NOT NULL
);
