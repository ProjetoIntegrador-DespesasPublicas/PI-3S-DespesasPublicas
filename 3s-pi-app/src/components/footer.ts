import { Component } from '@angular/core';

@Component({
  selector: 'footer-comp',
  standalone: true,
  template: `
    <footer class="footer">
      <p class="flex items-center justify-center min-w-sm">© {{ actualYear }} — Portal de Transparência Pública Orçamentária — Uso acadêmico.</p>
      <p class="text-[12px] flex items-center justify-center">
        Desenvolvido para fins educacionais, com foco na Transparência Pública de Dados Orçamentários. | API SOF v4 por Secretaria Municipal da Fazenda
      </p>
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