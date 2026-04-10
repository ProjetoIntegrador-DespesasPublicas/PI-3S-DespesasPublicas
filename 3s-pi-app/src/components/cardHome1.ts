import { Component, Input } from '@angular/core';

@Component({
  selector: 'card-home',
  standalone: true,
  template: `
    <section class="container">
      <div class="cardHomeContainer">
        <div class="item1">
          <h2 class="titleCard">Você sabe o que são despesas publicas?</h2>
          <p>
            Despesas públicas são o conjunto
            de gastos realizados pelo governo para atender as necessidades da sociedade e
            financiar serviços essenciais, como saúde, educação e infraestrutura.
          </p>
        </div>
        <div class="item2">
          <img class="image1" src="./src/assets/imagem1.jpg" />
        </div>
      </div>
    </section>
  `,
})
export class CardHomeComponent {}
