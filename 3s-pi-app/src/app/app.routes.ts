//import { Routes } from '@angular/router';
import { provideRouter, withHashLocation, RouterOutlet, RouterLink } from '@angular/router';


const routes = [
  { path: '', component: Home },
  { path: 'Consultar Despesas', component: consultarDespesas }
];

export const routes: Routes = [
providers: [provideRouter(routes, withHashLocation())]
];
