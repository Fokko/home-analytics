CREATE TABLE IF NOT EXISTS relay_state (
  created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
  A          BOOLEAN NOT NULL,
  B          BOOLEAN NOT NULL
)
