CREATE TABLE IF NOT EXISTS owners (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  api_key TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS widgets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL REFERENCES owners(id),
  public_id TEXT NOT NULL UNIQUE,
  type TEXT NOT NULL DEFAULT 'signup_form',
  title TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  button_text TEXT NOT NULL DEFAULT 'Submit',
  fields_json TEXT NOT NULL DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_widgets_owner_id ON widgets(owner_id);

CREATE TABLE IF NOT EXISTS submissions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  widget_public_id TEXT NOT NULL,
  owner_id INTEGER NOT NULL,
  data_json TEXT NOT NULL DEFAULT '{}',
  ip_address TEXT,
  geo_country TEXT,
  geo_city TEXT,
  geo_provider TEXT,
  idempotency_key TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_submissions_widget_public_id ON submissions(widget_public_id);
CREATE INDEX IF NOT EXISTS idx_submissions_owner_id ON submissions(owner_id);
CREATE INDEX IF NOT EXISTS idx_submissions_created_at ON submissions(created_at);

CREATE UNIQUE INDEX IF NOT EXISTS uq_submissions_idempotency
ON submissions(widget_public_id, idempotency_key)
WHERE idempotency_key IS NOT NULL;