import { Routes } from '@angular/router';
import { HomepageComponent } from '../pages/homepage';
import { DespesasPageComponent } from '../pages/consDespesas'

const routes: Routes = [
  { path: '', component: HomepageComponent },
  { path: 'despesas', component: DespesasPageComponent },
  // Add other routes as needed
];

export default routes;
