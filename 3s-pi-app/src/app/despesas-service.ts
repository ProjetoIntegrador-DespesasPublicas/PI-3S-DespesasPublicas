import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DespesasService {

  private API = 'http://localhost:8000'; // seu backend FastAPI

  constructor(private http: HttpClient) {}

  getResumo(): Observable<any> {
    return this.http.get(`${this.API}/despesas/resumo`);
  }

  getPorOrgao(): Observable<any[]> {
    return this.http.get<any[]>(`${this.API}/despesas/por-orgao`);
  }

  getTopCredores(): Observable<any[]> {
    return this.http.get<any[]>(`${this.API}/despesas/top-credores`);
  }

}