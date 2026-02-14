/**
 * Application configuration (env, DB, constants).
 * Same env vars as Django for compatibility.
 */

import dotenv from "dotenv";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: join(__dirname, "../../.env") });

export const config = {
  port: parseInt(process.env.EXPRESS_PORT || "8003", 10),
  host: process.env.EXPRESS_HOST || "0.0.0.0",
  workers: parseInt(process.env.EXPRESS_WORKERS || "1", 10),
  db: {
    host: process.env.DB_HOST || "localhost",
    port: parseInt(process.env.DB_PORT || "5432", 10),
    user: process.env.DB_USER || "postgres",
    password: process.env.DB_PASSWORD || "",
    database: process.env.DB_NAME || "bolt_test",
  },
  jwt: {
    secret: process.env.BOLT_JWT_SECRET || process.env.SECRET_KEY || "dev-secret",
    algorithm: process.env.BOLT_JWT_ALGORITHM || "HS256",
    expiresIn: parseInt(process.env.BOLT_JWT_EXPIRES_SECONDS || "3600", 10),
  },
};

export const ROLE_CHOICES = [
  { code: "ADMIN", name: "Administrator" },
  { code: "SHOPKEEPER", name: "Shopkeeper" },
  { code: "CUSTOMER", name: "Customer" },
];

export const VALID_ROLES = new Set(ROLE_CHOICES.map((r) => r.code));
