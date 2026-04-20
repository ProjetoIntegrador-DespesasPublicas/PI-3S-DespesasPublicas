import { Component } from '@angular/core';

@Component({
  selector: 'card-home',
  standalone: true,
  template: `
    <section class="welcome-card-wrapper">
      <div class="welcome-card">

        <div class="welcome-card-image">
          <img src="assets/imagem0.jpg" alt="Bem vindo ao portal" />
        </div>

        <div class="welcome-card-text">
          <h2>Bem vindo ao Portal de Transparência Pública</h2>
          <p>
            Acompanhe de forma simples e visual como os recursos públicos são aplicados,
            com foco nas despesas e empenhos realizados pelo governo.
          </p>
        </div>

      </div>
    </section>
  `
})
export class CardHomeComponent {}
