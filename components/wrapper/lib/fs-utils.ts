import {promises as fs} from 'fs';
import {resolve} from 'path';
import os from 'os';

export interface FSUtil {
  projectDir: string,
  tempDir: string
};

export async function init(): Promise<FSUtil> {
  const today = new Date();
  const month = (today.getMonth() + 1).toString().padStart(2, '0');
  const time = today.getHours();
  const hour = time > 12 ? `${time - 12}pm` : `${time}am`;

  const tmpFolder = resolve(os.tmpdir(), 'dphm');
  const dataFolder = resolve(os.homedir(), 'PHM');

  let status = await fs.stat(tmpFolder).catch(_ => null);

  if (!status) {
    await fs.mkdir(tmpFolder)
  }

  status = await fs.stat(dataFolder).catch(_ => null);

  if (!status) {
    await fs.mkdir(dataFolder);
  }

  const folderBase = `Run `;
  let folderSuffix = 0;
  let projectDir = resolve(dataFolder, folderBase + folderSuffix);
  let folderType = 0;

  while (!folderType) {
    folderSuffix++;
    projectDir = resolve(dataFolder, folderBase + folderSuffix);
    folderType = await fs.readdir(projectDir).then(f => f.length === 0 ? 2 : 0).catch(_ => 1);
  }

  // CASE: folder doesn't exist
  if (folderType === 1) {
    await fs.mkdir(projectDir);
  }

  return {
    projectDir,
    tempDir: tmpFolder
  };
}