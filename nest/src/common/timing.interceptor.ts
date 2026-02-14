import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { FastifyReply } from 'fastify';

@Injectable()
export class TimingInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const start = performance.now();
    const response = context.switchToHttp().getResponse<FastifyReply>();

    response.header('X-Server-Time', new Date().toISOString());

    return next.handle().pipe(
      tap(() => {
        const durationMs = (performance.now() - start).toFixed(2);
        if (!response.sent) {
          response.header('X-Response-Time', `${durationMs}ms`);
        }
      }),
    );
  }
}
