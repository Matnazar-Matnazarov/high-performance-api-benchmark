/**
 * Express.js API - Bolt-compatible endpoints.
 *
 * Same endpoints as Django Bolt: /health, /health/test, /ready, /roles, /users.
 * Uses PostgreSQL (same DB as Django). X-Server-Time, X-Response-Time on every response.
 *
 * Usage:
 *   npm start                    # single worker
 *   EXPRESS_WORKERS=4 npm start  # 4 workers (load test)
 *   node src/index.js
 *
 * Load test: EXPRESS_WORKERS=4 npm start
 *           ./loadtest -api express -duration 5s -concurrency 50
 */

import cluster from "cluster";
import express from "express";
import { config } from "./config.js";
import { timingMiddleware } from "./middleware/timing.js";
import docsRouter from "./routes/docs.js";
import healthRouter from "./routes/health.js";
import rolesRouter from "./routes/roles.js";
import usersRouter from "./routes/users.js";
import authRouter from "./routes/auth.js";

const workers = Math.max(1, config.workers);

if (cluster.isPrimary && workers > 1) {
  for (let i = 0; i < workers; i++) {
    cluster.fork();
  }
  cluster.on("exit", (worker) => {
    console.log(`Worker ${worker.process.pid} exited, restarting...`);
    cluster.fork();
  });
  console.log(`Express (Bolt-compatible) master: ${workers} workers on http://${config.host}:${config.port}`);
} else {
  const app = express();

  app.use(express.json());
  app.use(timingMiddleware);

  // API routes first (health, roles, users, auth)
  app.use(healthRouter);
  app.use(rolesRouter);
  app.use(usersRouter);
  app.use(authRouter);
  // Docs last (Swagger, ReDoc, Scalar)
  app.use(docsRouter);

  app.listen(config.port, config.host, () => {
    const pid = process.pid;
    const w = workers > 1 ? ` worker ${pid}` : "";
    console.log(`Express (Bolt-compatible)${w} listening on http://${config.host}:${config.port}`);
  });
}
