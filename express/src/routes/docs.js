/**
 * API docs: Swagger UI (/docs), ReDoc (/redoc), OpenAPI JSON (/openapi.json).
 * Spec is embedded in Swagger UI to avoid fetch issues (0.0.0.0, CORS).
 * Redirect 0.0.0.0 → localhost so Swagger UI assets load (Chrome blocks 0.0.0.0).
 */

import { Router } from "express";
import swaggerUi from "swagger-ui-express";
import { getOpenApiSpec } from "../openapi.js";

const router = Router();

// Redirect 0.0.0.0 → localhost (Chrome/brauzer 0.0.0.0 da Swagger UI yuklamaydi)
router.get(["/docs", "/docs/"], (req, res, next) => {
  const host = req.get("host") || "";
  if (host.startsWith("0.0.0.0")) {
    const port = host.includes(":") ? host.split(":")[1] : "8003";
    return res.redirect(302, `http://localhost:${port}/docs/`);
  }
  next();
});

// OpenAPI JSON (dynamic base URL)
router.get("/openapi.json", (req, res) => {
  res.json(getOpenApiSpec(req));
});

// Middleware: inject spec per-request (dynamic baseUrl)
function injectSpec(req, res, next) {
  req.swaggerDoc = getOpenApiSpec(req);
  next();
}

const swaggerOptions = {
  swaggerOptions: {
    persistAuthorization: true,
    displayRequestDuration: true,
  },
};

// Swagger UI at /docs — spec embedded, no fetch
router.use(
  "/docs",
  injectSpec,
  swaggerUi.serveFiles(null, swaggerOptions),
  swaggerUi.setup(null, swaggerOptions)
);

// ReDoc at /redoc
router.get("/redoc", (req, res) => {
  res.send(`
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Express API - ReDoc</title>
  <link href="https://cdn.jsdelivr.net/npm/redoc@2.3.0/bundles/redoc.standalone.css" rel="stylesheet">
</head>
<body>
  <redoc spec-url="/openapi.json"></redoc>
  <script src="https://cdn.jsdelivr.net/npm/redoc@2.3.0/bundles/redoc.standalone.js"></script>
</body>
</html>
  `);
});

// Scalar at /scalar (modern API reference)
router.get("/scalar", (req, res) => {
  const baseUrl = `${req.protocol}://${req.get("host")}`;
  const specUrl = `${baseUrl}/openapi.json`;
  res.send(`
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Express API - Scalar</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@scalar/api-reference"/>
</head>
<body>
  <div id="app"></div>
  <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
  <script>
    Scalar.createApiReference('#app', { url: '${specUrl}' });
  </script>
</body>
</html>
  `);
});

export default router;
