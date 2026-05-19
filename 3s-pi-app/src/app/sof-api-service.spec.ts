import { TestBed } from '@angular/core/testing';

import { SofApiService } from './sof-api-service';

describe('SofApiService', () => {
  let service: SofApiService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SofApiService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
