/**
 * Auth routes: POST /auth/login (JWT, Bolt-compatible format).
 * Returns: access_token, expires_in, token_type.
 * Verifies Django PBKDF2 password hashes.
 */

import { Router } from "express";
import { pbkdf2Sync } from "crypto";
import jwt from "jsonwebtoken";
import { query } from "../db.js";
import { config } from "../config.js";

const router = Router();

/** Verify Django pbkdf2_sha256 password hash. */
function verifyDjangoPassword(password, hash) {
  if (!hash || !hash.startsWith("pbkdf2_sha256$")) {
    return false;
  }
  const [, iterationsStr, saltB64, expectedB64] = hash.split("$");
  const iterations = parseInt(iterationsStr, 10);
  if (!iterations || !saltB64 || !expectedB64) return false;

  const salt = Buffer.from(saltB64.replace(/\./g, "+"), "base64");
  const expected = Buffer.from(expectedB64.replace(/\./g, "+"), "base64");
  const derived = pbkdf2Sync(
    password,
    salt,
    iterations,
    32,
    "sha256"
  );
  return Buffer.compare(derived, expected) === 0;
}

router.post("/auth/login", async (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) {
    return res.status(400).json({ detail: "username and password required" });
  }

  const result = await query(
    "SELECT id, username, password FROM accounts_user WHERE username = $1",
    [username.trim()]
  );
  const user = result.rows[0];
  if (!user || !verifyDjangoPassword(password, user.password)) {
    return res.status(401).json({ detail: "Invalid credentials" });
  }

  const accessToken = jwt.sign(
    { sub: String(user.id) },
    config.jwt.secret,
    {
      algorithm: config.jwt.algorithm,
      expiresIn: config.jwt.expiresIn,
    }
  );

  res.json({
    access_token: accessToken,
    expires_in: config.jwt.expiresIn,
    token_type: "bearer",
  });
});

export default router;
