const STUBBED = false;
const execa = require('execa');

const delay = (time: number) => new Promise(resolve => setTimeout(resolve, time));

export default abstract class BaseComponentConnector {
  abstract prepareArguments(...args: any[]): [];

  abstract processResult(result: string): any;

  abstract command: string;

  async exec(...passthrough: any[]) {
    if (STUBBED) {
      const args = this.prepareArguments(...passthrough);

      const {stdout} = await execa(this.command, args);

      return this.processResult(stdout);
    }

    await delay(Number(this.command));
  }
}