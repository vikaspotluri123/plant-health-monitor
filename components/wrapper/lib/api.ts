import {resolve} from 'path';
import EventEmitter from 'events';
import * as connectors from './connectors';
import * as fsUtils from './fs-utils';
import instance from './drone-connection';

let folderReadyPromise: Promise<fsUtils.FSUtil>;
let folders: fsUtils.FSUtil;

export const events = new EventEmitter();

export function emitMessage(message: any, data: any = null) {
  return events.emit('action', message, data);
}

instance.events.on('connection.lost', () => emitMessage('drone.disconnected'));
instance.events.on('connection.restored', () => emitMessage('drone.connected'));

export async function determineWaypoints(a: string, b: string, c: string, d: string) {
  return await connectors.routing.exec(a, b, c, d);
}

export async function init() {
  folderReadyPromise = fsUtils.init();
  folders = await folderReadyPromise;
}

export async function flyOver(a: string, b: string, c: string, d: string) {
  console.log('Starting flyover');
  // Step 1: determine waypoints
  await determineWaypoints(a, b, c, d);
  emitMessage('routingCompleted');
  // Step 2: upload waypoints to drone
  // await connectors.analysis.exec('upload');
  // emitMessage('routesUploaded');
  // Step 3: fly baby fly!
  // This will probably be tied to the WiFi library (we're waiting to be reconnected via WiFi)
  await connectors.navigation.exec();
  emitMessage('navigationComplete');
}

export async function processImages(letter: string) {
  await folderReadyPromise;
  const tempDir = `"${folders.tempDir}"`;
  const copyDest = `"${resolve(folders.projectDir, 'ingest')}"`.replace(/\/\//g, '');
  const stitchedFile = `"${resolve(folders.projectDir, 'stitched.jpg')}"`.replace(/\/\//g, '');
  const analyzedFile =  `"${resolve(folders.projectDir, 'analyzed.jpg')}"`.replace(/\/\//g, '');

  emitMessage('copyingData');
  await connectors.clone.exec(letter, copyDest);
  emitMessage('dataCopied');

  await connectors.stitching.exec(copyDest, stitchedFile, tempDir);
  emitMessage('stichingCompleted', stitchedFile);

  await connectors.analysis.exec(stitchedFile, analyzedFile);
  emitMessage('imageProcessed', analyzedFile);
}

export function isConnected() {
  return instance.isConnected;
}