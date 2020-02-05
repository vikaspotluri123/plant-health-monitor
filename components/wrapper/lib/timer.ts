import {performance} from 'perf_hooks'

export class Timer {
  start = -1;

  constructor() {
    this.reset();
  }

  reset(): void {
    this.start = performance.now();
  }

  next(): number {
    const initial = performance.now();
    this.reset();
    return this.start - initial;
  }
}

export default new Timer();