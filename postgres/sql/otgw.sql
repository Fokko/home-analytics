CREATE TABLE IF NOT EXISTS otgw (
  created_at          TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
  relative_mod_level  DOUBLE PRECISION NOT NULL,
  control_setpoint    DOUBLE PRECISION NOT NULL,
  ch_water_temp       DOUBLE PRECISION NOT NULL,
  slave_flame_on      BOOLEAN NOT NULL,
  slave_ch_active     BOOLEAN NOT NULL
);
