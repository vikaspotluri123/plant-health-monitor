import Base from './base';

export default class RoutingConnector extends Base {
  command = '1600';

  prepareArguments(): [] {
    return [];
  }

  processResult(result: string): string {
    return result;
  }
}