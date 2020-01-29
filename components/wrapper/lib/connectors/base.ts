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

      try {
        console.log(`Running ${this.command} ${args.join(' ')}`);
        const {stdout} = await execa(this.command, args);

        return this.processResult(stdout);
      } catch (error) {
        console.log(error);
        return;
      }
    }

    console.log('Not implemented, delaying', this.command);
    await delay(Number(this.command));
  }
}