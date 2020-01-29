import {resolve} from 'path';
import Base from './base';

export default class AnalysisConnector extends Base {
  implemented = true;

  command = 'python3';

  prepareArguments(basePath: string): any[] {
    const input = `"${resolve(basePath, 'stitching.jpg')}"`;
    const output = `"${resolve(basePath, 'analyzed.jpg')}"`;

    return ['../analysis/main.py', input, output];
  }

  processResult(result: string): string {
    return result;
  }
}