/**
 * Role routes: /roles, /roles/code/:code (Bolt-compatible).
 */

import { Router } from "express";
import { ROLE_CHOICES } from "../config.js";

const router = Router();

router.get("/roles", (req, res) => {
  res.json(ROLE_CHOICES.map((r) => ({ code: r.code, name: r.name })));
});

router.get("/roles/code/:code", (req, res) => {
  const code = (req.params.code || "").trim().toUpperCase();
  const role = ROLE_CHOICES.find((r) => r.code === code);
  if (!role) {
    return res.status(404).json({ detail: "Role not found" });
  }
  res.json({ code: role.code, name: role.name });
});

export default router;
