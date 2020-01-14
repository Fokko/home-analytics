SET timezone = 'Europe/Amsterdam';

CREATE TABLE IF NOT EXISTS solar (
  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
  ac_watt          INT NOT NULL,
  dc_volt          DOUBLE PRECISION NOT NULL,
  dc_amps          DOUBLE PRECISION NOT NULL,
  ac_volts         DOUBLE PRECISION NOT NULL,
  ac_amps          DOUBLE PRECISION NOT NULL,
  ac_freq          DOUBLE PRECISION NOT NULL,
  temp             DOUBLE PRECISION NOT NULL
);
