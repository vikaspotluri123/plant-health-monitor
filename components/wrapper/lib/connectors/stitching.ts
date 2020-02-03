import {resolve} from 'path';
import Base from './base';

export default class StitchingConnector extends Base {
  implemented = true;

  command = 'python3';

  prepareArguments(basePath: string, tempDir: string): any[] {
    const input = `"${resolve(basePath, 'ingest')}"`.replace(/\/\//g, '');
    const output = `"${resolve(basePath, 'stitched.jpg')}"`.replace(/\/\//g, '');
    const temp = `"${tempDir}"`;

    return ['../stitching/stitching.py', input, output, 2, 2, temp];
  }

  processResult(result: string): string {
    return result;
  }
}