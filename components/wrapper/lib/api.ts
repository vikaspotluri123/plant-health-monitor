import {resolve} from 'path';
import EventEmitter from 'events';
import * as connectors from './connectors';
import * as fsUtils from './fs-utils';
import instance from './drone-connection';
import timer from './timer';

let folderReadyPromise: Promise<fsUtils.FSUtil>;
let folders: fsUtils.FSUtil;

export const events = new EventEmitter();

export function emitMessage(message: any, data: any = null) {
  return events.emit('action', message, data);
}

instance.events.on('connection.lost', () => emitMessage('drone.disconnected'));
instance.events.on('connection.restored', () => emitMessage('drone.connected'));

export async function determineWaypoints(a: string, b: string, c: string, d: string, _resetTimer = true) {
  _resetTimer && timer.reset();
  const response = await connectors.routing.exec(a, b, c, d);

  if (response[connectors.EXEC_ERROR]) {
    emitMessage('error', ['determine_waypoints', response.stderr]);
    return null;
  }

  return {
    time: timer.next(),
    points: response
  }
}

export async function init() {
  folderReadyPromise = fsUtils.init();
  folders = await folderReadyPromise;
}

export async function flyOver(a: string, b: string, c: string, d: string) {
  console.log('Starting flyover');
  timer.reset();
  // Step 1: determine waypoints
  const response = await determineWaypoints(a, b, c, d, false);

  if (!response) {
    return;
  }

  emitMessage('routingCompleted', response);
  // Step 2: upload waypoints to drone
  // await connectors.analysis.exec('upload');
  // emitMessage('routesUploaded');
  // Step 3: fly baby fly!
  // This will probably be tied to the WiFi library (we're waiting to be reconnected via WiFi)
  const res2 = await connectors.navigation.exec();

  if (res2 && res2[connectors.EXEC_ERROR] === true) {
    return emitMessage('error', ['determine_waypoints', res2.stderr]);
  }

  emitMessage('navigationComplete', {time: timer.next()});
}

export async function processImages(letter: string) {
  timer.reset();
  await folderReadyPromise;
  const tempDir = `"${folders.tempDir}"`;
  const copyDest = `"${resolve(folders.projectDir, 'ingest')}"`.replace(/\/\//g, '');
  const stitchedFile = `"${resolve(folders.projectDir, 'stitched.jpg')}"`.replace(/\/\//g, '');
  const analyzedFile =  `"${resolve(folders.projectDir, 'analyzed.jpg')}"`.replace(/\/\//g, '');

  emitMessage('copyingData', {time: timer.next()});
  let res = await connectors.clone.exec(letter, copyDest);

  if (res && res[connectors.EXEC_ERROR] === true) {
    return emitMessage('error', ['copy_data', res.stderr]);
  }

  emitMessage('dataCopied', {time: timer.next()});

  res = await connectors.stitching.exec(copyDest, stitchedFile, tempDir);

  if (res && res[connectors.EXEC_ERROR] === true) {
    return emitMessage('error', ['run_stitching', res.stderr]);
  }

  emitMessage('stichingCompleted', {image: stitchedFile, time: timer.next()});

  res = await connectors.analysis.exec(stitchedFile, analyzedFile);

  if (res && res[connectors.EXEC_ERROR] === true) {
    return emitMessage('error', ['run_analysis', res.stderr]);
  }

  emitMessage('imageProcessed', {image: analyzedFile, time: timer.next()});
}

export function isConnected() {
  return instance.isConnected;
}