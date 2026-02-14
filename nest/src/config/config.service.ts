import { Injectable } from '@nestjs/common';
import { config, Config, ROLE_CHOICES, VALID_ROLES } from './config';

@Injectable()
export class ConfigService {
  private readonly _config: Config;

  constructor() {
    this._config = config();
  }

  get port(): number {
    return this._config.port;
  }

  get host(): string {
    return this._config.host;
  }

  get workers(): number {
    return this._config.workers;
  }

  get db() {
    return this._config.db;
  }

  get jwt() {
    return this._config.jwt;
  }

  get ROLE_CHOICES() {
    return ROLE_CHOICES;
  }

  get VALID_ROLES() {
    return VALID_ROLES;
  }
}
