/* central table holdings */
CREATE TABLE IF NOT EXISTS tables (
  table_id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_name TEXT NOT NULL UNIQUE,
  returned INTEGER DEFAULT 0
);

/* work assignments */
CREATE TABLE IF NOT EXISTS assignments (
  table_id INTEGER NOT NULL,
  client TEXT NOT NULL,
  requestTime INTEGER,
  returnTime  INTEGER DEFAULT NULL,
  result TEXT DEFAULT NULL,
  error  TEXT DEFAULT NULL
);


/* CEA targets + results */
CREATE TABLE IF NOT EXISTS cea (
  table_id INTEGER NOT NULL,
  row_id INTEGER NOT NULL,
  col_id INTEGER NOT NULL,
  mapped TEXT DEFAULT NULL,
  PRIMARY KEY (table_id, row_id, col_id)
);


/* CPA targets + results */
CREATE TABLE IF NOT EXISTS cpa (
  table_id INTEGER NOT NULL,
  sub_id INTEGER NOT NULL,
  obj_id INTEGER NOT NULL,
  mapped TEXT DEFAULT NULL,
  PRIMARY KEY (table_id, sub_id, obj_id)
);


/* CTA targets + results */
CREATE TABLE IF NOT EXISTS cta (
  table_id INTEGER NOT NULL,
  col_id INTEGER NOT NULL,
  mapped TEXT DEFAULT NULL,
  PRIMARY KEY (table_id, col_id)
);
