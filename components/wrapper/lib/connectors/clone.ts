import assert from 'assert';

const DRIVE_LETTERS = ['d', 'e', 'f', 'g'];

const delay = (time: number) => new Promise(resolve => setTimeout(resolve, time));

export default class AnalysisConnector {
    async exec(drive: string, outputFolder: string) {
        assert(DRIVE_LETTERS.includes(drive), 'Invalid drive');

        // @todo: implement real logic here
        await delay(1200);

        return 'C:\\code\\plant-health-monitor\\img\\for-stitch';
    }
}