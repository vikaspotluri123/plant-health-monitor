import Base from './base';

export default class StitchingConnector extends Base {
  implemented = true;

  command = 'python3';

  prepareArguments(...args: any[]): any[] {
    return ['../stitching/stitching.py', ...args];
  }

  processResult(result: string): string {
    return result;
  }
}