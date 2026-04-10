import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HomepageComponent } from "../pages/homepage";

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, HomepageComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('3s-pi-app');
}
