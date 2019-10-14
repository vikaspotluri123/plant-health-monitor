import Base from './base';

export default class AnalysisConnector extends Base {
  command = '2250';

  prepareArguments(): [] {
    return [];
  }

  processResult(result: string): string {
    return result;
  }
}