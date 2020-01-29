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

  const folderBase = `${today.getFullYear()}-${month}-${today.getDate()} ${hour} Run `;
  let folderSuffix = 1;
  let docFolder;

  do {
    docFolder = resolve(dataFolder, folderBase + folderSuffix);
    folderSuffix++;
  } while (await fs.stat(docFolder).catch(_ => null));

  await fs.mkdir(docFolder);

  return {
    projectDir: docFolder,
    tempDir: tmpFolder
  };
}