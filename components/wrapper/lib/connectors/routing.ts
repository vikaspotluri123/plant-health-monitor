import Base from './base';

export default class RoutingConnector extends Base {
  implemented = true;

  command = 'python3';

  prepareArguments(...args: any[]): any[] {
    return ['../routing/routing.py', ...args];
  }

  processResult(result: string): string[][] {
    return result.split('\n').map(a => a.trim().split(','));
  }
}