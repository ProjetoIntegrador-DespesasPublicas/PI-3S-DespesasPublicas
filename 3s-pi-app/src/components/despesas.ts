import {
  Component,
  OnInit,
  OnDestroy,
  PLATFORM_ID,
  Inject,
} from '@angular/core';
import { CommonModule }        from '@angular/common';
import { FormsModule }         from '@angular/forms';
import { isPlatformBrowser }   from '@angular/common';
import { Subject }             from 'rxjs';
import { takeUntil, finalize } from 'rxjs/operators';

import {
  DespesasService,
  MesDisponivel,
  DashboardData,
  Resumo,
  ItemOrgao,
  ItemCredor,
  ItemPrograma,
} from '../app/despesas-service';

@Component({
  selector:    'app-despesas',
  standalone:  true,
  imports:     [CommonModule, FormsModule],
  templateUrl: './despesasComponent.html',
  styleUrls:   ['./despesasComponent.css'],
})
export class DespesasComponent implements OnInit, OnDestroy {

  // ──────────────────────────────────────────
  // DADOS
  // ──────────────────────────────────────────

  resumo: Resumo = {
    ano: 2026, mes: 0,
    orcado: 0, empenhado: 0, liquidado: 0, pago: 0,
  };
  porOrgao:     ItemOrgao[]    = [];
  topCredores:  ItemCredor[]   = [];
  topProgramas: ItemPrograma[] = [];

  // ──────────────────────────────────────────
  // UI
  // ──────────────────────────────────────────

  loading      = false;
  loadingMeses = false;
  erro: string | null = null;
  temDados     = false;

  readonly ano = 2026;

  // ──────────────────────────────────────────
  // FILTRO
  // ──────────────────────────────────────────

  mesSelecionado    = 0;
  mesesDisponiveis: MesDisponivel[] = [];

  get nomeMes(): string {
    return this.mesesDisponiveis.find(m => m.valor === this.mesSelecionado)?.nome ?? '';
  }

  // ──────────────────────────────────────────
  // INTERNO
  // ──────────────────────────────────────────

  private destroy$  = new Subject<void>();
  private isBrowser: boolean;

  constructor(
    private service: DespesasService,
    @Inject(PLATFORM_ID) platformId: object,
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  // ──────────────────────────────────────────
  // LIFECYCLE
  // ──────────────────────────────────────────

  ngOnInit(): void {
    // Não executa nada no servidor — evita pending tasks no SSR
    if (!this.isBrowser) return;
    this.carregarMeses();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // ──────────────────────────────────────────
  // PÚBLICO (template)
  // ──────────────────────────────────────────

  aplicarFiltro(): void {
    if (!this.mesSelecionado || this.loading) return;
    this.service.clearCache();
    this.loadDashboard();
  }

  // ──────────────────────────────────────────
  // PRIVADOS
  // ──────────────────────────────────────────

  private carregarMeses(): void {
    this.loadingMeses = true;

    this.service
      .getMesesDisponiveis()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: resp => {
          this.mesesDisponiveis = resp.meses ?? [];
          this.mesSelecionado   = resp.mes_padrao;
          this.loadingMeses     = false;
          this.loadDashboard();
        },
        error: (err: Error) => {
          this.loadingMeses = false;
          this.erro = `Falha ao carregar meses: ${err.message}`;
        },
      });
  }

  private loadDashboard(): void {
    if (!this.mesSelecionado || this.loading) return;

    this.loading = true;
    this.erro    = null;

    this.service
      .getDashboard(this.mesSelecionado)
      .pipe(
        takeUntil(this.destroy$),
        finalize(() => (this.loading = false)),
      )
      .subscribe({
        next: (data: DashboardData) => {
          // Persiste no cache do service
          this.service.setCache(this.mesSelecionado, data);

          this.resumo       = data.resumo       ?? this.resumo;
          this.porOrgao     = data.porOrgao     ?? [];
          this.topCredores  = data.topCredores  ?? [];
          this.topProgramas = data.topProgramas ?? [];
          this.temDados     = true;

          console.table({
            orgaos:    this.porOrgao.length,
            credores:  this.topCredores.length,
            programas: this.topProgramas.length,
          });
        },
        error: (err: Error) => {
          this.erro = err.message;
          console.error('[DespesasComponent]', err);
        },
      });
  }
}