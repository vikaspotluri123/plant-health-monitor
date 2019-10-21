import {EventEmitter} from 'events';
import {isIPv4} from 'net';

import ping from './ping';

export class DroneConnection {
  public events: EventEmitter = new EventEmitter();

  private connectionAddr: string;

  private connected = false;

  constructor(ip: string) {
    if (!isIPv4(ip)) {
      throw new Error('Invalid ip');
    }

    this.connectionAddr = ip;
    this.ping();
  }

  async ping(): Promise<void> {
    console.log('pinging');
    const canConnect = await ping(this.connectionAddr);

    if (canConnect) {
      if (!this.connected) {
        this.connected = true;
        this.events.emit('connection.restored');
      }

      return;
    }

    if (this.connected) {
      this.connected = false;
      this.events.emit('connection.lost');
    }

    // @todo: check if we need to unref this
    setTimeout(() => this.ping(), 1000 * 15);
  }
}

const instance = new DroneConnection('192.168.1.101');

export default instance;