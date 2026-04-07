import { Component, Input } from '@angular/core';

@Component({
  selector: 'footer-comp',
  standalone: true,
  template: `
    <section class="flex">
      <div class="cardHomeContainer">
        <div class="item1">
          <h2>Você sabe o que são despesas publicas?</h2>
          <p>
            Despesas públicas são o conjunto
            de gastos realizados pelo governo para atender as necessidades da sociedade e
            financiar serviços essenciais, como saúde, educação e infraestrutura.
          </p>
        </div>
        <div class="item2">
          <img src="3s-pi-appsrcassetsimagem1.jpg" />
        </div>
      </div>
    </section>
  `,
})
export class card1Component {}
