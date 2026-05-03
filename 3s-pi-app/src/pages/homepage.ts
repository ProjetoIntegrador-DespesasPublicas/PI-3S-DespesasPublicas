import { Component } from '@angular/core';
import { FooterComponent } from '../components/footer';
import { HeaderComponent } from '../components/header';
import { CardHomeComponent } from '../components/cardHome2';
@Component({
  selector: 'app-homepage',
  standalone: true,
  imports: [FooterComponent, HeaderComponent, CardHomeComponent],
    template: `
    <div class="homepage">
      <header-comp class="headerComp"></header-comp>
      <card-home class="cardHomeComp"></card-home>
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
export class HomepageComponent {}


