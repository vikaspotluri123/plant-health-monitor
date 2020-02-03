import Base from './base';

export default class StitchingConnector extends Base {
  implemented = true;

  command = 'python3';

  prepareArguments(input: string, output: string, temp: string): any[] {
    return ['../stitching/stitching.py', input, output, 2, 2, temp];
  }

  processResult(result: string): string {
    return result;
  }
}