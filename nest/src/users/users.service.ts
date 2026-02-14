import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { DatabaseService } from '../database/database.service';
import { ConfigService } from '../config/config.service';

export interface User {
  id: number;
  username: string;
  role: string;
}

export interface UserListResult {
  results: User[];
  count: number;
  next: string | null;
  previous: string | null;
}

@Injectable()
export class UsersService {
  constructor(
    private readonly db: DatabaseService,
    private readonly config: ConfigService,
  ) {}

  async list(
    search: string,
    role: string,
    page: number,
    pageSize: number,
  ): Promise<UserListResult> {
    const conditions: string[] = [];
    const params: unknown[] = [];
    let idx = 1;

    if (search?.trim()) {
      conditions.push(`username ILIKE $${idx}`);
      params.push(`%${search.trim()}%`);
      idx++;
    }
    if (role && this.config.VALID_ROLES.has(role as 'ADMIN' | 'SHOPKEEPER' | 'CUSTOMER')) {
      conditions.push(`role = $${idx}`);
      params.push(role);
      idx++;
    }

    const whereClause = conditions.length ? conditions.join(' AND ') : '1=1';
    const offset = (page - 1) * pageSize;

    const countResult = await this.db.query<{ cnt: number }>(
      `SELECT COUNT(*)::int AS cnt FROM accounts_user WHERE ${whereClause}`,
      params,
    );
    const total = countResult.rows[0]?.cnt ?? 0;

    const dataResult = await this.db.query<{ id: number; username: string; role: string }>(
      `SELECT id, username, role FROM accounts_user
       WHERE ${whereClause}
       ORDER BY id
       LIMIT $${idx} OFFSET $${idx + 1}`,
      [...params, pageSize, offset],
    );

    const results = dataResult.rows.map((r) => ({
      id: r.id,
      username: r.username,
      role: r.role || 'CUSTOMER',
    }));

    const nextUrl =
      offset + results.length < total
        ? `?page=${page + 1}&page_size=${pageSize}`
        : null;
    const prevUrl = page > 1 ? `?page=${page - 1}&page_size=${pageSize}` : null;

    return { results, count: total, next: nextUrl, previous: prevUrl };
  }

  async getById(id: number): Promise<User> {
    const result = await this.db.query<{ id: number; username: string; role: string }>(
      'SELECT id, username, role FROM accounts_user WHERE id = $1',
      [id],
    );
    const row = result.rows[0];
    if (!row) {
      throw new NotFoundException({ detail: 'User not found' });
    }
    return {
      id: row.id,
      username: row.username,
      role: row.role || 'CUSTOMER',
    };
  }
}
