import { Injectable, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '../config/config.service';
import { Pool } from 'pg';

@Injectable()
export class DatabaseService implements OnModuleDestroy {
  private pool: Pool;

  constructor(private config: ConfigService) {
    const db = this.config.db;
    this.pool = new Pool({
      host: db.host,
      port: db.port,
      user: db.user,
      password: db.password,
      database: db.database,
      max: db.max ?? 20,
      idleTimeoutMillis: db.idleTimeoutMillis ?? 30000,
      connectionTimeoutMillis: db.connectionTimeoutMillis ?? 10000,
    });
  }

  async query<T = unknown>(text: string, params?: unknown[]): Promise<{ rows: T[]; rowCount: number }> {
    const client = await this.pool.connect();
    try {
      const result = await client.query(text, params);
      return { rows: result.rows as T[], rowCount: result.rowCount ?? 0 };
    } finally {
      client.release();
    }
  }

  async healthCheck(): Promise<boolean> {
    const { rowCount } = await this.query('SELECT 1');
    return rowCount > 0;
  }

  async onModuleDestroy() {
    await this.pool.end();
  }
}
