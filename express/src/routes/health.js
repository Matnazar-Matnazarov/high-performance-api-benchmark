/**
 * Health routes: /health, /health/test, /ready (Bolt-compatible).
 */

import { Router } from "express";
import { healthCheck } from "../db.js";

const router = Router();

router.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

router.get("/health/test", (req, res) => {
  res.json({
    status: "ok",
    message: "Test health check endpoint",
  });
});

router.get("/ready", async (req, res) => {
  try {
    await healthCheck();
    res.json({ status: "healthy", checks: { database: "ok" } });
  } catch {
    res.status(503).json({
      status: "unhealthy",
      checks: { database: "error" },
    });
  }
});

export default router;
