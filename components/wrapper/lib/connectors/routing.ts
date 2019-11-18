import Base from './base';

export default class RoutingConnector extends Base {
  implemented = true;

  command = 'python';

  prepareArguments(...args: any[]): any[] {
    return ['../routing/routing.py', ...args];
  }

  processResult(result: string): string {
    console.log('Got result', result);
    return result;
  }
}