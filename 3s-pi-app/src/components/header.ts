import { Component, Input } from '@angular/core';

@Component({
  selector: 'header-comp',
  standalone: true,
  template: `
    <header class="flex items-start">
      <div class="h-(--header) flex-auto">
        <div class="menu">
          <h4 class="tittle">Portal de Transparência Pública Orçamentária</h4>
          <ul>
            <li><a href="#">Home</a></li>
            <li><a href="#">Consultar Despesas</a></li>
            <li><a href="#">Consultar Empenhos</a></li>
            <li><a href="#">Favoritos</a></li>
          </ul>
        </div>
      </div>
    </header>
  `,
})
export class HeaderComponent {}
