import Base from './base';
import { PathLike } from 'fs';
const delay = (time: number) => new Promise(resolve => setTimeout(resolve, time));

export default class AnalysisConnector extends Base {
  command = '2250';

  prepareArguments(): [] {
    return [];
  }

  processResult(result: string): string {
    return result;
  }

  async exec(inputDir: PathLike): Promise<PathLike> {
    console.log('Processing image in', inputDir);
    await delay(1000);
    return 'C:\\code\\plant-health-monitor\\img\\for-processing\\processed.png';
  }
}