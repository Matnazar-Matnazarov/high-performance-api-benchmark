import { Controller, Post, Body } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBody } from '@nestjs/swagger';
import { AuthService } from './auth.service';

class LoginDto {
  username!: string;
  password!: string;
}

@ApiTags('Auth')
@Controller('auth')
export class AuthController {
  constructor(private readonly auth: AuthService) {}

  @Post('login')
  @ApiOperation({ summary: 'Login (JWT)' })
  @ApiBody({ type: LoginDto })
  async login(@Body() body: { username?: string; password?: string }) {
    return this.auth.login(body.username || '', body.password || '');
  }
}
