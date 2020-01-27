import Base from './base';

export default class AnalysisConnector extends Base {
  implemented = true;

  command = 'python3';

  prepareArguments(...args: any[]): any[] {
    return ['../analysis/main.py', ...args];
  }

  processResult(result: string): string {
    return result;
  }
}