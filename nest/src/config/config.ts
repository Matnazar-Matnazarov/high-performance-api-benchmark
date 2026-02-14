import { config as loadEnv } from 'dotenv';
import { join } from 'path';

// Load .env from project root (same as Django/Express)
loadEnv({ path: join(__dirname, '../../../.env') });

/**
 * Application config. Same env vars as Django/Express.
 */
export const config = () => ({
  port: parseInt(process.env.NEST_PORT || '8004', 10),
  host: process.env.NEST_HOST || '0.0.0.0',
  workers: parseInt(process.env.NEST_WORKERS || '1', 10),
  db: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432', 10),
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'bolt_test',
    max: 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 10000,
  },
  jwt: {
    secret: process.env.BOLT_JWT_SECRET || process.env.SECRET_KEY || 'dev-secret',
    algorithm: (process.env.BOLT_JWT_ALGORITHM || 'HS256') as 'HS256',
    expiresIn: parseInt(process.env.BOLT_JWT_EXPIRES_SECONDS || '3600', 10),
  },
});

export type Config = ReturnType<typeof config>;

export const ROLE_CHOICES = [
  { code: 'ADMIN', name: 'Administrator' },
  { code: 'SHOPKEEPER', name: 'Shopkeeper' },
  { code: 'CUSTOMER', name: 'Customer' },
] as const;

export const VALID_ROLES = new Set(ROLE_CHOICES.map((r) => r.code));
