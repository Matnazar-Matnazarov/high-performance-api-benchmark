import { Injectable, UnauthorizedException, BadRequestException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { DatabaseService } from '../database/database.service';
import { ConfigService } from '../config/config.service';
import { pbkdf2Sync } from 'crypto';

/** Verify Django pbkdf2_sha256 password hash. */
function verifyDjangoPassword(password: string, hash: string): boolean {
  if (!hash || !hash.startsWith('pbkdf2_sha256$')) {
    return false;
  }
  const parts = hash.split('$');
  const iterationsStr = parts[1];
  const saltB64 = parts[2];
  const expectedB64 = parts[3];
  const iterations = parseInt(iterationsStr, 10);
  if (!iterations || !saltB64 || !expectedB64) return false;

  const salt = Buffer.from(saltB64.replace(/\./g, '+'), 'base64');
  const expected = Buffer.from(expectedB64.replace(/\./g, '+'), 'base64');
  const derived = pbkdf2Sync(password, salt, iterations, 32, 'sha256');
  return Buffer.compare(derived, expected) === 0;
}

@Injectable()
export class AuthService {
  constructor(
    private readonly db: DatabaseService,
    private readonly jwt: JwtService,
    private readonly config: ConfigService,
  ) {}

  async login(username: string, password: string) {
    if (!username?.trim() || !password) {
      throw new BadRequestException({ detail: 'username and password required' });
    }

    const result = await this.db.query<{ id: number; username: string; password: string }>(
      'SELECT id, username, password FROM accounts_user WHERE username = $1',
      [username.trim()],
    );
    const user = result.rows[0];
    if (!user || !verifyDjangoPassword(password, user.password)) {
      throw new UnauthorizedException({ detail: 'Invalid credentials' });
    }

    const accessToken = this.jwt.sign(
      { sub: String(user.id) },
      {
        secret: this.config.jwt.secret,
        algorithm: this.config.jwt.algorithm,
        expiresIn: this.config.jwt.expiresIn,
      },
    );

    return {
      access_token: accessToken,
      expires_in: this.config.jwt.expiresIn,
      token_type: 'bearer',
    };
  }
}
