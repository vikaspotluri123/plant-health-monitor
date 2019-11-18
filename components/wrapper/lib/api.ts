import EventEmitter from 'events';
import * as connectors from './connectors';
import instance from './drone-connection';

export const events = new EventEmitter();

export function emitMessage(message: any, data: any = null) {
  return events.emit('action', message, data);
}

instance.events.on('connection.lost', () => emitMessage('drone.disconnected'));
instance.events.on('connection.restored', () => emitMessage('drone.connected'));

export async function flyOver(a: string, b: string, c: string, d: string) {
  console.log('Starting flyover');
  // Step 1: determine waypoints
  await connectors.routing.exec(a, b, c, d);
  emitMessage('routingCompleted');
  // Step 2: upload waypoints to drone
  await connectors.routing.exec('upload');
  emitMessage('routesUploaded');
  // Step 3: fly baby fly!
  // This will probably be tied to the WiFi library (we're waiting to be reconnected via WiFi)
  await connectors.navigation.exec();
  emitMessage('navigationComplete');
}

export async function processImages(letter: string) {
  emitMessage('copyingData');
  const inputDir = await connectors.clone.exec(letter);
  emitMessage('dataCopied');

  const stitchedFilePath = await connectors.stitching.exec(inputDir);
  emitMessage('stichingCompleted', stitchedFilePath);

  const colorizedFilePath = await connectors.analysis.exec(stitchedFilePath);
  emitMessage('imageProcessed', colorizedFilePath);
}

export function isConnected() {
  return instance.isConnected;
}

if (!module.parent) {
  connectors.routing.exec('96.40788589416512,30.55456066156509', '-96.40702758728003,30.55456066156509', '-96.40702758728003,30.553969358102023', '-96.4078858941651,30.553969358102023')
    .then(c => console.log(c));
}