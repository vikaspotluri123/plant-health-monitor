import assert from 'assert';
import {promises as fs, Stats, PathLike} from 'fs';
import path from 'path';
import {EXEC_ERROR} from './base';

const DRIVE_LETTERS = ['d', 'e', 'f', 'g'];

async function getAllFiles(source: string): Promise<string[]> {
    const fileList: string[] = [];

    for (const file of await fs.readdir(source)) {
        const fullPath = path.resolve(source, file);
        const stats = await fs.stat(fullPath);

        if (stats.isDirectory()) {
            fileList.push(...await getAllFiles(fullPath))
        } else {
            fileList.push(fullPath);
        }
    }

    return fileList;
}

export default class AnalysisConnector {
    async exec(drive: string, outputFolder: string) {
        outputFolder = outputFolder.replace(/"/g, '');
        assert(DRIVE_LETTERS.includes(drive), 'Invalid drive');
        const fromDir = `${drive}:\\\\demo-pics`; // @todo: determine camera output
        const outStat = await fs.stat(outputFolder).catch(_ => null);

        if (!outStat) {
            await fs.mkdir(outputFolder);
        }

        const folderStats = await fs.stat(fromDir).catch(_ => null);

        if (!folderStats || !folderStats.isDirectory()) {
            return {
                [EXEC_ERROR]: true,
                stdout: '',
                stderr: 'ENOSRCDIR'
            };
        }

        const files = await getAllFiles(fromDir);

        for (const file of files) {
            const relPath = path.relative(fromDir, file)
            const outputFile = path.resolve(outputFolder, relPath);
            await fs.copyFile(file, outputFile)
        }

        return true;
    }
}