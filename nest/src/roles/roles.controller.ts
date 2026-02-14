import { Controller, Get, Param, NotFoundException } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { ConfigService } from '../config/config.service';

@ApiTags('Roles')
@Controller('roles')
export class RolesController {
  constructor(private readonly config: ConfigService) {}

  @Get()
  @ApiOperation({ summary: 'List roles' })
  list() {
    return this.config.ROLE_CHOICES.map((r) => ({ code: r.code, name: r.name }));
  }

  @Get('code/:code')
  @ApiOperation({ summary: 'Get role by code' })
  getByCode(@Param('code') code: string) {
    const role = this.config.ROLE_CHOICES.find(
      (r) => r.code === (code || '').trim().toUpperCase(),
    );
    if (!role) {
      throw new NotFoundException({ detail: 'Role not found' });
    }
    return { code: role.code, name: role.name };
  }
}
