/**
 * User routes: /users (list, paginated), /users/:id (Bolt-compatible).
 * Same DB table as Django: accounts_user.
 */

import { Router } from "express";
import { query } from "../db.js";
import { VALID_ROLES } from "../config.js";

const router = Router();

router.get("/users", async (req, res) => {
  const search = (req.query.search || "").trim();
  const role = (req.query.role || req.query.role_code || "").trim().toUpperCase();
  const page = Math.max(1, parseInt(req.query.page, 10) || 1);
  const pageSize = Math.min(100, Math.max(1, parseInt(req.query.page_size, 10) || 10));

  const conditions = [];
  const params = [];
  let idx = 1;

  if (search) {
    conditions.push(`username ILIKE $${idx}`);
    params.push(`%${search}%`);
    idx++;
  }
  if (role && VALID_ROLES.has(role)) {
    conditions.push(`role = $${idx}`);
    params.push(role);
    idx++;
  }

  const whereClause = conditions.length ? conditions.join(" AND ") : "1=1";
  const offset = (page - 1) * pageSize;

  const countResult = await query(
    `SELECT COUNT(*)::int AS cnt FROM accounts_user WHERE ${whereClause}`,
    params
  );
  const total = countResult.rows[0]?.cnt ?? 0;

  const dataResult = await query(
    `SELECT id, username, role FROM accounts_user
     WHERE ${whereClause}
     ORDER BY id
     LIMIT $${idx} OFFSET $${idx + 1}`,
    [...params, pageSize, offset]
  );

  const results = dataResult.rows.map((r) => ({
    id: r.id,
    username: r.username,
    role: r.role || "CUSTOMER",
  }));

  const nextUrl =
    offset + results.length < total
      ? `?page=${page + 1}&page_size=${pageSize}`
      : null;
  const prevUrl = page > 1 ? `?page=${page - 1}&page_size=${pageSize}` : null;

  res.json({
    results,
    count: total,
    next: nextUrl,
    previous: prevUrl,
  });
});

router.get("/users/:id", async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (isNaN(id)) {
    return res.status(400).json({ detail: "Invalid user ID" });
  }

  const result = await query(
    "SELECT id, username, role FROM accounts_user WHERE id = $1",
    [id]
  );
  const row = result.rows[0];
  if (!row) {
    return res.status(404).json({ detail: "User not found" });
  }

  res.json({
    id: row.id,
    username: row.username,
    role: row.role || "CUSTOMER",
  });
});

export default router;
