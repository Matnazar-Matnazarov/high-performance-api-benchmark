/**
 * PostgreSQL connection pool (pg).
 * Same database as Django - accounts_user table.
 */

import pg from "pg";
import { config } from "./config.js";

const pool = new pg.Pool({
  host: config.db.host,
  port: config.db.port,
  user: config.db.user,
  password: config.db.password,
  database: config.db.database,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 10000,
});

export async function query(text, params) {
  const client = await pool.connect();
  try {
    return await client.query(text, params);
  } finally {
    client.release();
  }
}

export async function healthCheck() {
  const result = await query("SELECT 1");
  return result.rowCount > 0;
}

export { pool };
