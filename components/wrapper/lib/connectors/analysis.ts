import {resolve} from 'path';
import Base from './base';

export default class AnalysisConnector extends Base {
  implemented = true;

  command = 'python3';

  prepareArguments(input: string, output: string): any[] {
    return ['../analysis/main.py', input, output];
  }

  processResult(result: string): string {
    return result;
  }
}