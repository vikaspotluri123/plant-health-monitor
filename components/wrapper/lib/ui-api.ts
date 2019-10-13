import EventEmitter from 'events';

const delay = (time: number) => new Promise(resolve => setTimeout(resolve, time));

export const events = new EventEmitter();

export async function flyOver(a: string, b: string, c: string, d: string) {
  await delay(1600);
  events.emit('routingCompleted');
  await delay(2560);
  events.emit('routesUploaded');
  await delay(25000);
  events.emit('navigationComplete');
  await delay(2250);
  events.emit('mediaInserted');
}