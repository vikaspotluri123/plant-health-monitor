import Base from './base';

export default class StitchingConnector extends Base {
  command = '5000';

  prepareArguments(): [] {
    return [];
  }

  processResult(result: string): string {
    return result;
  }
}