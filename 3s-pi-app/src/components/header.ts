import { Component, Input } from '@angular/core';

@Component({
  selector: 'header-comp',
  standalone: true,
  template: `
    <header class="flex items-start">
    <div class="bg-header h-(--header) flex-auto">
        <h4>Portal de Transparência Pública Orçamentária</h4>
        <p>Home</p>
    </div>
    </header>
`,
})
export class HeaderComponent {}
