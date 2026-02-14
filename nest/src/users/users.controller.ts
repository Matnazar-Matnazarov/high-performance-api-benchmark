import {
  Controller,
  Get,
  Param,
  Query,
  ParseIntPipe,
  BadRequestException,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiQuery } from '@nestjs/swagger';
import { UsersService } from './users.service';

@ApiTags('Users')
@Controller('users')
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Get()
  @ApiOperation({ summary: 'List users' })
  @ApiQuery({ name: 'search', required: false })
  @ApiQuery({ name: 'role', required: false, enum: ['ADMIN', 'SHOPKEEPER', 'CUSTOMER'] })
  @ApiQuery({ name: 'role_code', required: false })
  @ApiQuery({ name: 'page', required: false })
  @ApiQuery({ name: 'page_size', required: false })
  async list(
    @Query('search') search = '',
    @Query('role') roleParam?: string,
    @Query('role_code') roleCode?: string,
    @Query('page') pageParam?: string,
    @Query('page_size') pageSizeParam?: string,
  ) {
    const role = (roleParam || roleCode || '').trim().toUpperCase();
    const page = Math.max(1, parseInt(pageParam || '1', 10) || 1);
    const pageSize = Math.min(100, Math.max(1, parseInt(pageSizeParam || '10', 10) || 10));
    return this.users.list(search, role, page, pageSize);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get user by ID' })
  async getById(@Param('id', ParseIntPipe) id: number) {
    if (isNaN(id)) {
      throw new BadRequestException({ detail: 'Invalid user ID' });
    }
    return this.users.getById(id);
  }
}
