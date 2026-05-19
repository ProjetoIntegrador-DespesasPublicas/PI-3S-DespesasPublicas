import { Component } from '@angular/core';
import { DashboardComponent } from '../components/dashboard.component';
import { FooterComponent } from '../components/footer';
import { HeaderComponent } from '../components/header';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [FooterComponent, HeaderComponent, DashboardComponent],
  styleUrls: ['../components/dashboard.component.scss'],
  template: `
    <div class="dashboard-page">
      <header-comp class="headerComp"></header-comp>
      <app-dashboard class="dashboardComp"></app-dashboard>
      <footer-comp class="footerComp"></footer-comp>
    </div>
  `,
})
export class DashboardPageComponent {}
