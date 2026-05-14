import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';

@Component({
  selector: 'card-home',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="min-h-[95vh] flex items-center justify-center bg-gray-150 p-20">
      <div class="relative w-full max-w-8xl">
        <!-- Slides -->
        <div class="overflow-hidden rounded-lg shadow-lg">
          <div
            class="flex transition-transform duration-500 ease-in-out"
            [style.transform]="'translateX(-' + currentIndex * 100 + '%)'"
          >
            <!-- Card 1 -->
            <div class="min-w-full grid grid-cols-1 md:grid-cols-2 gap-8 bg-white p-6">
              <div class="flex flex-col justify-center">
                <h1 class="text-2xl font-bold text-gray-800 mb-4 text-lg text-center">
                  Bem vindo ao Portal de Transparencia Publica
                </h1>
                <p class=" textCard text-gray-950 leading-relaxed text-lg ">
                  Acompanhe de forma simples e visual como os recursos públicos são aplicados, com
                  foco nas despesas e empenhos realizados pelo governo.
                </p>
              </div>
              <div
                class="flex items-center flex justify-center-safe p-px24 h-auto w-full max-w-320px"
              >
                <img
                  src="img0.png"
                  alt="Imagem 1"
                  class="rounded-lg shadow-md max-h-100 object-cover"
                />
              </div>
            </div>

            <!-- Card 2 -->
            <div class="min-w-full grid grid-cols-1 md:grid-cols-2 gap-8 bg-white p-6">
              <div class="flex flex-col justify-center">
                <h1 class="text-2xl font-bold text-gray-800 mb-4 text-lg text-center">
                  Você sabe o que são despesas publicas?
                </h1>
                <p class="textCard text-gray-950 leading-relaxed text-lg">
                  Despesas públicas são o conjunto de gastos realizados pelo governo para atender as
                  necessidades da sociedade e financiar serviços essenciais, como saúde, educação e
                  infraestrutura.
                </p>
              </div>
              <div class="flex items-center flex justify-center-safe">
                <img
                  src="imagem1.jpg"
                  alt="Imagem 2"
                  class="rounded-lg shadow-md max-h-320px object-cover h-auto w-full"
                />
              </div>
            </div>

            <!-- Card 3 -->
            <div class="min-w-full grid grid-cols-1 md:grid-cols-2 gap-8 bg-white p-6">
              <div class="flex flex-col justify-center">
                <h1 class="text-2xl font-bold text-gray-800 mb-4 text-lg text-center">
                  Você sabe o que são Empenhos?
                </h1>
                <p class="textCard text-gray-950 leading-relaxed text-lg">
                  São a quantidade de dinheiro que será pago quando o bem for entregue
                  ou o serviço concluído. Issofaz com que o orgão publico organize os gastos pelas
                  diferentes áreas, evitando que se gaste mais do que foi planejado.
                </p>
              </div>
              <div class="flex items-center flex justify-center-safe h-auto w-full max-w-320px">
                <img
                  src="imagem2.jpg"
                  alt="Imagem 3"
                  class="rounded-lg shadow-md max-h-80 object-cover"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Botões de navegação -->
        <div class="buttonPage absolute inset-0 flex items-center justify-between ">
          <button
            (click)="prev()"
            class="bg-gray-800 text-white p-2 rounded-full hover:bg-gray-600"
          >
            <a class="color: text-blue-400 bg-transparent"><</a>
          </button>
          <button
            (click)="next()"
            class="bg-gray-800 text-white p-2 rounded-full hover:bg-gray-600"
          >
            <a class="text-blue-400">></a>
          </button>
        </div>

        <!-- Indicadores -->
        <div class="flex justify-center mt-4 space-x-2">
          <button
            *ngFor="let slide of slides; let i = index"
            (click)="goToSlide(i)"
            class="w-3 h-3 rounded-full"
            [class.bg-gray-800]="i === currentIndex"
            [class.bg-gray-400]="i !== currentIndex"
          ></button>
        </div>
      </div>
    </div>
  `,
})
export class CardHomeComponent implements OnInit, OnDestroy {
  currentIndex = 0;
  slides = [0, 1, 2];
  intervalId: any;

  ngOnInit() {
    this.startAutoPlay();
  }

  ngOnDestroy() {
    this.clearAutoPlay();
  }

  startAutoPlay() {
    this.intervalId = setInterval(() => {
      this.next();
    }, 5000);
  }

  clearAutoPlay() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  next() {
    this.currentIndex = (this.currentIndex + 1) % this.slides.length;
  }

  prev() {
    this.currentIndex = (this.currentIndex - 1 + this.slides.length) % this.slides.length;
  }

  goToSlide(index: number) {
    this.currentIndex = index;
    this.startAutoPlay();
  }
}
