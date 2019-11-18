const execa = require('execa');

const delay = (time: number) => new Promise(resolve => setTimeout(resolve, time));

export default abstract class BaseComponentConnector {

  implemented: boolean = false;

  abstract prepareArguments(...args: any[]): any[];

  abstract processResult(result: string): any;

  abstract command: string;

  async exec(...passthrough: any[]) {
    if (this.implemented) {
      const args = this.prepareArguments(...passthrough);
      console.log('running');

      const {stdout} = await execa(this.command, args);

      console.log('ran');
      return this.processResult(stdout);
    }

    await delay(Number(this.command));
  }
}