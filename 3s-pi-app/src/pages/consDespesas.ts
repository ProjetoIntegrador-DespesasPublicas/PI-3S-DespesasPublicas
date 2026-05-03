import { Component } from '@angular/core';
import { FooterComponent } from '../components/footer';
import { HeaderComponent } from '../components/header';
import { DespesasComponent } from '../components/despesas';

@Component({
  selector: 'app-despesas-page',
  standalone: true,
  imports: [FooterComponent, HeaderComponent, DespesasComponent],
    template: `
    <div class="homepage">
      <header-comp class="headerComp"></header-comp>

      <app-despesas></app-despesas>

      <footer-comp class="footerComp"></footer-comp>
    </div>
  `,
  styles: [`
    .homepage {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    .footerComp{
        margin-top: auto;
        width: auto;
    }
    .cardHomeComp{
        width: auto;
        padding: 10px;
        position: relative;
        align-content: center;
    }

    .headerComp{
        width: auto;
    }
  `]
})
export class DespesasPageComponent {}


