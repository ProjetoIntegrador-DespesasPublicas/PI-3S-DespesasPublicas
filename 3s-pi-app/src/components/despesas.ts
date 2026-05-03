import { Component, OnInit } from '@angular/core';
import { DespesasService } from '../app/despesas-service';
import { forkJoin } from 'rxjs';
import { CommonModule } from '@angular/common'

@Component({
  selector: 'app-despesas',
  templateUrl: './despesasComponent.html',
  imports: [ CommonModule ],
  styleUrls: ['./despesasComponent.css']
})
export class DespesasComponent implements OnInit {

  resumo: any = {};
  porOrgao: any[] = [];
  topCredores: any[] = [];

  loading = true;

  constructor(private service: DespesasService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData() {
    this.loading = true;

    forkJoin({
      resumo: this.service.getResumo(),
      orgao: this.service.getPorOrgao(),
      credores: this.service.getTopCredores()
    }).subscribe({
      next: (result) => {
        this.resumo = result.resumo;
        this.porOrgao = result.orgao || [];
        this.topCredores = result.credores || [];
      },
      error: (err) => {
        console.error('Erro ao carregar dados:', err);
      },
      complete: () => {
        this.loading = false;
      }
    });
  }
}