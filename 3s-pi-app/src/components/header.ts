import { Component } from '@angular/core';

@Component({
  selector: 'header-comp',
  standalone: true,
  template: `
    <header class="header-bar">

      <span class="header-title">Portal de Transparência Pública</span>

      <nav class="header-nav">
        <a href="#" class="nav-item nav-active">Início</a>
        <a href="despesas" class="nav-item">Consultar Despesas</a>
        <a href="#" class="nav-item">Consultar Empenhos</a>
        <a href="#" class="nav-item">Favoritos</a>
      </nav>

      <button class="theme-btn" (click)="toggleTheme()">
        {{ isDark ? '☀' : '☾' }}
      </button>

    </header>
  `
})
export class HeaderComponent {
  isDark = false;

  toggleTheme() {
    this.isDark = !this.isDark;
    document.documentElement.classList.toggle('dark', this.isDark);
  }
}