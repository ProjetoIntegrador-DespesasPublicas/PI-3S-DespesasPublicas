import { Component } from '@angular/core';

@Component({
  selector: 'header-comp',
  standalone: true,
  template: `
    <header class="header-bar">

      <span class="header-title">Portal de Transparência Pública</span>

      <nav class="header-nav">
        <a href="#" class="nav-item nav-active">Home</a>
        <a href="#" class="nav-item">Consultar Despesas</a>
        <a href="#" class="nav-item">Consultar Empenhos</a>
        <a href="#" class="nav-item">Favoritos</a>
      </nav>

      <button class="theme-btn" (click)="toggleTheme()">
        {{ isDark ? '☀' : '☾' }}
      </button>

    </header>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
    }

    .header-bar {
      width: 100%;
      height: 44px;
      display: flex;
      align-items: center;
      padding: 0 24px;
      box-sizing: border-box;
      background-color: #f0f2f4;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18), 0 1px 3px rgba(0, 0, 0, 0.12);
    }

    .header-title {
      font-size: 0.88rem;
      font-weight: 600;
      color: var(--color-footer);
      white-space: nowrap;
      flex-shrink: 0;
    }

    .header-nav {
      display: flex;
      align-items: center;
      justify-content: space-evenly;
      flex: 1;
      height: 100%;
      margin: 0 16px;
    }

    .nav-item {
      display: flex;
      align-items: center;
      height: 100%;
      padding: 0 16px;
      font-size: 0.88rem;
      color: #4a5568;
      text-decoration: none;
      white-space: nowrap;
      border-bottom: 2px solid transparent;
      box-sizing: border-box;
      transition: background-color 0.2s ease,
                  color 0.2s ease,
                  border-bottom-color 0.2s ease;
    }

    .nav-active {
      background-color: #e8f0fe;
      color: var(--color-footer);
      border-bottom: 2px solid var(--color-footer);
    }

    .nav-item:hover {
      background-color: #dde3ea;
      color: var(--color-footer);
      border-bottom-color: var(--color-footer);
    }

    .theme-btn {
      width: 32px;
      height: 32px;
      border: none;
      border-radius: 50%;
      background-color: var(--color-footer);
      color: #ffffff;
      font-size: 1rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: filter 0.2s ease;
    }

    .theme-btn:hover {
      filter: brightness(1.15);
    }

    :host-context(.dark) .header-bar {
      background-color: #1e2533;
    }

    :host-context(.dark) .header-title {
      color: #90caf9;
    }

    :host-context(.dark) .nav-item {
      color: #cbd5e0;
    }

    :host-context(.dark) .nav-active {
      background-color: #1a2f4a;
      color: #90caf9;
      border-bottom-color: #90caf9;
    }

    :host-context(.dark) .nav-item:hover {
      background-color: #1a2f4a;
      color: #90caf9;
      border-bottom-color: #90caf9;
    }

    :host-context(.dark) .theme-btn {
      background-color: #003d72;
    }
  `]
})
export class HeaderComponent {
  isDark = false;

  toggleTheme() {
    this.isDark = !this.isDark;
    document.documentElement.classList.toggle('dark', this.isDark);
  }
}