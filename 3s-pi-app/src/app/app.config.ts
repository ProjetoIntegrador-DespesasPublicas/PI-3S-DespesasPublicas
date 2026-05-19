import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter }                                  from '@angular/router';
import { provideClientHydration }                         from '@angular/platform-browser';
import {
  provideHttpClient,
  withFetch,
  withInterceptors,
  HttpInterceptorFn,
  HttpHandlerFn,
  HttpRequest,
}                                                         from '@angular/common/http';
import { inject }                                         from '@angular/core';
import { PendingTasks }                                   from '@angular/core';

import  routes             from './app.routes';
import { SKIP_SSR_PENDING }  from './despesas-service';

/**
 * Interceptor que impede o Angular SSR de manter requisições
 * marcadas com SKIP_SSR_PENDING como "pending tasks".
 *
 * Sem isso, o HttpClient no servidor aguarda cada resposta
 * antes de considerar a aplicação "estável", causando o erro:
 * "Application did not stabilize within 9 seconds"
 */
const skipSsrPendingInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
) => {
  if (req.context.get(SKIP_SSR_PENDING)) {
    // Remove a requisição da fila de pending tasks do SSR
const pendingTasks = inject(PendingTasks);

const cleanup = pendingTasks.add();

const result = next(req);

// Finaliza imediatamente a pending task
cleanup();

return result;
  }
  return next(req);
};

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideClientHydration(),
    provideHttpClient(
      withFetch(),
      withInterceptors([skipSsrPendingInterceptor]),
    ),
  ],
};