import { NestFactory } from '@nestjs/core';
import {
  FastifyAdapter,
  NestFastifyApplication,
} from '@nestjs/platform-fastify';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { ConfigService } from './config/config.service';

async function bootstrap() {
  const app = await NestFactory.create<NestFastifyApplication>(
    AppModule,
    new FastifyAdapter(),
  );

  const config = app.get(ConfigService);

  // Swagger
  const swaggerConfig = new DocumentBuilder()
    .setTitle('NestJS API (Bolt-compatible)')
    .setDescription(
      'Same endpoints as Django Bolt. Health, Roles, Users, Auth. JWT via POST /auth/login. Use **Authorize** to add Bearer token.',
    )
    .setVersion('0.1.0')
    .addBearerAuth(
      {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
        description: 'JWT from POST /auth/login',
      },
      'BearerAuth',
    )
    .addServer(`http://localhost:${config.port}`, 'API server')
    .build();

  const document = SwaggerModule.createDocument(app, swaggerConfig);
  SwaggerModule.setup('docs', app, document, {
    swaggerOptions: {
      persistAuthorization: true,
      displayRequestDuration: true,
    },
  });

  await app.listen(config.port, config.host);
  console.log(
    `NestJS (Bolt-compatible) listening on http://${config.host}:${config.port}`,
  );
  console.log(`Swagger: http://localhost:${config.port}/docs`);
}

bootstrap();
