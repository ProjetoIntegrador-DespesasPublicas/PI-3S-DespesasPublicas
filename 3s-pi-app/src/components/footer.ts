import { Component } from '@angular/core';

@Component({
  selector: 'footer-comp',
  standalone: true,
  template: `
    <footer class="footer">
      <p>© {{ actualYear }} — Portal de Transparência Pública Orçamentária — Uso acadêmico.</p>
      <p>Desenvolvido para fins educacionais, com foco na Transparência Pública de Dados Orçamentários.</p>
    </footer>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
    }
  `]
})
export class FooterComponent {
  actualYear: number = new Date().getFullYear();
}