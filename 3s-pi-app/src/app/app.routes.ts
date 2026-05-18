import { Routes } from '@angular/router';
import { HomepageComponent } from '../pages/homepage';
import { DespesasPageComponent } from '../pages/consDespesas';
import { DashboardComponent } from '../components/dashboard.component';

const routes: Routes = [
  { path: '', component: HomepageComponent },
  { path: 'despesas', component: DespesasPageComponent },
  { path: 'dashboard', component: DashboardComponent },
  // Add other routes as needed
];

export default routes;
