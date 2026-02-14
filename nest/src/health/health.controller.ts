import { Controller, Get, HttpException, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { DatabaseService } from '../database/database.service';

@ApiTags('Health')
@Controller()
export class HealthController {
  constructor(private readonly db: DatabaseService) {}

  @Get('health')
  @ApiOperation({ summary: 'Liveness' })
  health() {
    return { status: 'ok' };
  }

  @Get('health/test')
  @ApiOperation({ summary: 'Custom health check' })
  healthTest() {
    return { status: 'ok', message: 'Test health check endpoint' };
  }

  @Get('ready')
  @ApiOperation({ summary: 'Readiness (DB)' })
  async ready() {
    try {
      const ok = await this.db.healthCheck();
      if (!ok) throw new Error('DB check failed');
      return { status: 'healthy', checks: { database: 'ok' } };
    } catch {
      throw new HttpException(
        { status: 'unhealthy', checks: { database: 'error' } },
        HttpStatus.SERVICE_UNAVAILABLE,
      );
    }
  }
}
