import {
  Injectable,
  OnDestroy,
  PLATFORM_ID,
  Inject,
} from '@angular/core';
import {
  HttpClient,
  HttpParams,
  HttpErrorResponse,
  HttpContext,
  HttpContextToken,
} from '@angular/common/http';
import { isPlatformBrowser }          from '@angular/common';
import { Observable, of, throwError, Subject, EMPTY } from 'rxjs';
import { catchError, takeUntil }      from 'rxjs/operators';

// ==============================
// Token que informa ao Angular SSR
// para NÃO bloquear a estabilização
// nessa requisição HTTP.
// Compatível com Angular 17+.
// ==============================
export const SKIP_SSR_PENDING = new HttpContextToken<boolean>(() => false);

// ==============================
// INTERFACES
// ==============================

export interface MesDisponivel {
  valor: number;
  nome:  string;
}

export interface MesesResponse {
  ano:        number;
  mes_padrao: number;
  meses:      MesDisponivel[];
}

export interface Resumo {
  ano:       number;
  mes:       number;
  orcado:    number;
  empenhado: number;
  liquidado: number;
  pago:      number;
}

export interface ItemOrgao {
  orgao:    string;
  codOrgao: string | number;
  valor:    number;
}

export interface ItemCredor {
  credor: string;
  valor:  number;
}

export interface ItemPrograma {
  programa:    string;
  codPrograma: string | number;
  valor:       number;
}

export interface DashboardMeta {
  ano:                  number;
  mes:                  number;
  registros_dotacoes:   number;
  orgaos_retornados:    number;
  credores_retornados:  number;
  programas_retornados: number;
}

export interface DashboardData {
  meta:         DashboardMeta;
  resumo:       Resumo;
  porOrgao:     ItemOrgao[];
  topCredores:  ItemCredor[];
  topProgramas: ItemPrograma[];
}

// ==============================
// CACHE LOCAL (dados resolvidos)
// ==============================

interface CacheEntry {
  data:      DashboardData;
  expiresAt: number;
}

// ==============================
// SERVICE
// ==============================

@Injectable({ providedIn: 'root' })
export class DespesasService implements OnDestroy {

  private readonly API       = 'https://pi-3s-despesaspublicas.onrender.com';
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutos

  private dashboardCache = new Map<number, CacheEntry>();
  private destroy$       = new Subject<void>();
  private isBrowser:     boolean;

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) platformId: object,
  ) {
    // SSR guard — só executa requisições no browser
    this.isBrowser = isPlatformBrowser(platformId);
  }

  // ──────────────────────────────────────────
  // CONTEXTO HTTP — evita SSR pending tasks
  // ──────────────────────────────────────────

  /**
   * Cria um HttpContext que instrui o Angular a NÃO
   * contabilizar esta requisição como "pending task" no SSR,
   * resolvendo o erro "did not stabilize within 9 seconds".
   */
  private get noSsrContext(): HttpContext {
    return new HttpContext().set(SKIP_SSR_PENDING, true);
  }

  // ──────────────────────────────────────────
  // MESES DISPONÍVEIS
  // ──────────────────────────────────────────

  getMesesDisponiveis(): Observable<MesesResponse> {
    if (!this.isBrowser) return EMPTY;

    return this.http
      .get<MesesResponse>(`${this.API}/meses-disponiveis`, {
        context: this.noSsrContext,
      })
      .pipe(
        catchError(this.handleError),
        takeUntil(this.destroy$),
      );
  }

  // ──────────────────────────────────────────
  // DASHBOARD
  // ──────────────────────────────────────────

  getDashboard(mes: number): Observable<DashboardData> {
    if (!this.isBrowser) return EMPTY;

    // Cache local — retorna imediatamente se válido
    const cached = this.dashboardCache.get(mes);
    if (cached && Date.now() < cached.expiresAt) {
      return of(cached.data);
    }

    const params = new HttpParams().set('mes', mes.toString());

    return this.http
      .get<DashboardData>(`${this.API}/despesas/dashboard`, {
        params,
        context: this.noSsrContext,
      })
      .pipe(
        catchError(this.handleError),
        takeUntil(this.destroy$),
      );
  }

  /** Salva resultado no cache após receber do backend. */
  setCache(mes: number, data: DashboardData): void {
    this.dashboardCache.set(mes, {
      data,
      expiresAt: Date.now() + this.CACHE_TTL,
    });
  }

  clearCache(): void {
    this.dashboardCache.clear();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // ──────────────────────────────────────────
  // TRATAMENTO DE ERROS
  // ──────────────────────────────────────────

  private handleError(error: HttpErrorResponse): Observable<never> {
    const msgs: Record<number, string> = {
      0:   'Sem conexão com o servidor. Verifique se o backend está rodando.',
      400: 'Mês selecionado ainda não tem dados disponíveis.',
      502: 'Erro ao comunicar com a SOF API. Tente novamente.',
      504: 'A SOF API demorou demais para responder.',
    };
    const msg = msgs[error.status] ?? `Erro (${error.status}): ${error.message}`;
    return throwError(() => new Error(msg));
  }
}