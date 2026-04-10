import { Component, Input } from '@angular/core';

@Component({
  selector: 'footer-comp',
  standalone: true,
  template: `
    <footer class="flex items-end">
      <div class="footer">
        <p>© {{ actualYear }} — Portal de Transparência Pública Orçamentária — Uso acadêmico.</p>
        <p>Desenvolvido para fins educacionais, com foco na Transparência Pública de Dados Orçamentários.</p>
      </div>
    </footer>
  `,
})
export class FooterComponent {
  actualYear: number = new Date().getFullYear();
}
