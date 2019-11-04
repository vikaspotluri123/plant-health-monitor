import Base from './base';
import {PathLike} from 'fs';

const delay = (time: number) => new Promise(resolve => setTimeout(resolve, time));

export default class StitchingConnector extends Base {
  command = '5000';

  prepareArguments(): [] {
    return [];
  }

  processResult(result: string): string {
    return result;
  }

  async exec(inputDir: PathLike): Promise<PathLike> {
    console.log('Processing data in', inputDir);
    await delay(5000);
    return 'C:\\code\\plant-health-monitor\\img\\for-processing\\img.jpg';
  }
}