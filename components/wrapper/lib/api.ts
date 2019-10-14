import EventEmitter from 'events';
import * as connectors from './connectors';

export const events = new EventEmitter();

export async function flyOver(a: string, b: string, c: string, d: string) {
  console.log('Starting flyover');
  // Step 1: determine waypoints
  await connectors.routing.exec(a, b, c, d);
  events.emit('routingCompleted');
  // Step 2: upload waypoints to drone
  await connectors.routing.exec('upload');
  events.emit('routesUploaded');
  // Step 3: fly baby fly!
  // This will probably be tied to the Bluetooth library (we're waiting to be reconnected via bluetooth)
  await connectors.navigation.exec();
  events.emit('navigationComplete');
  // Step 4: we've reconnected to the drone, wait for SD card to be inserted
  await connectors.routing.exec();
  events.emit('mediaInserted');
  console.log('Flyover complete');
}