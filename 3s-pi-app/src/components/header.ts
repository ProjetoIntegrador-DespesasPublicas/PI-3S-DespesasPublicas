import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'header-comp',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <header class="header-bar">

      <span class="header-title">Portal de Transparência Pública</span>

      <nav class="header-nav">
        <a
            routerLink="/"
            routerLinkActive="nav-active"
            [routerLinkActiveOptions]="{ exact: true }"
            class="nav-item"
          >
          Início
        </a>

        <a
          routerLink="/despesas"
          routerLinkActive="nav-active"
          class="nav-item"
        >
          Consultar Despesas
        </a>

        <!-- <a
          routerLink="/empenhos"
          routerLinkActive="nav-active"
          class="nav-item"
        >
          Consultar Empenhos
        </a> -->
      </nav>

      <!-- Barra de acessibilidade -->
      <div class="accessibility-bar">

        <button
          class="theme-btn"
          (click)="decreaseFontSize()"
          aria-label="Diminuir tamanho da fonte"
          title="Diminuir fonte">
          A-
        </button>

        <button
          class="theme-btn"
          (click)="increaseFontSize()"
          aria-label="Aumentar tamanho da fonte"
          title="Aumentar fonte">
          A+
        </button>

        <button
          class="theme-btn"
          (click)="toggleLibras()"
          [attr.aria-pressed]="isLibrasActive"
          [class.active-btn]="isLibrasActive"
          aria-label="Ativar interpretação em Libras"
          title="Libras">
          👋
        </button>

        <button
          class="theme-btn"
          (click)="toggleNarration()"
          [attr.aria-pressed]="isNarrating"
          [class.active-btn]="isNarrating"
          aria-label="Ativar narração da página"
          title="Narração">
          🔊
        </button>

        <button
          class="theme-btn"
          (click)="toggleTheme()"
          aria-label="Alternar modo claro e escuro"
          title="Alternar tema">
          {{ isDark ? '☀' : '☾' }}
        </button>

      </div>

    </header>
  `
})
export class HeaderComponent {

  // ── Tema ─────────────────────────────────────────────
  isDark = false;

  toggleTheme() {
    this.isDark = !this.isDark;
    document.documentElement.classList.toggle('dark', this.isDark);
  }

  // ── Tamanho da fonte ──────────────────────────────────
  private fontStep = 2;
  private readonly fontSteps = [12, 14, 16, 18, 20, 22];

  increaseFontSize() {
    if (this.fontStep < this.fontSteps.length - 1) {
      this.fontStep++;
      this.applyFontSize();
    }
  }

  decreaseFontSize() {
    if (this.fontStep > 0) {
      this.fontStep--;
      this.applyFontSize();
    }
  }

  private applyFontSize() {
    document.documentElement.style.fontSize =
      this.fontSteps[this.fontStep] + 'px';
  }

  // ── Libras ────────────────────────────────────────────
  isLibrasActive = false;

  toggleLibras() {
    this.isLibrasActive = !this.isLibrasActive;

    const widgetWrapper = document.querySelector('[vw]') as HTMLElement;

    if (widgetWrapper) {
      widgetWrapper.style.display = this.isLibrasActive ? 'block' : 'none';
    }
  }

  // ── Narração ──────────────────────────────────────────
  isNarrating = false;

  toggleNarration() {
    this.isNarrating = !this.isNarrating;

    if (!this.isNarrating) {
      window.speechSynthesis.cancel();
      return;
    }

    const text = document.body.innerText || document.body.textContent || '';
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pt-BR';
    utterance.rate = 1;
    utterance.onend = () => { this.isNarrating = false; };
    window.speechSynthesis.speak(utterance);
  }
}