import {EventEmitter} from 'events';
import {isIPv4} from 'net';

import ping from './ping';

// @const POLLING_INTERVAL = 15;
const POLLING_INTERVAL = 1;

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

  get isConnected() {
    return this.connected;
  }

  async ping(): Promise<void> {
    console.log('pinging');
    let canConnect = await ping(this.connectionAddr);
    // @todo: remove randomness
    canConnect = Math.random() <= 0.5;

    if (canConnect) {
      if (!this.connected) {
        this.connected = true;
        this.events.emit('connection.restored');
      }
    } else if (this.connected) {
      this.connected = false;
      this.events.emit('connection.lost');
    }

    // @todo: check if we need to unref this
    setTimeout(() => this.ping(), 1000 * POLLING_INTERVAL);
  }
}

const instance = new DroneConnection('192.168.1.101');

export default instance;