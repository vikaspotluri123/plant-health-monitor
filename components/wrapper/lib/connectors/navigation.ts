import Base from './base';

export default class NavigationConnector extends Base {
  command = '10000';

  prepareArguments(): [] {
    return [];
  }

  processResult(result: string): string {
    return result;
  }
}