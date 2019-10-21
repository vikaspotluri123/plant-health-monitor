import {TIMEOUT} from './constants';
const run = require('net-ping');

const session = run.createSession({timeout: TIMEOUT});

export default function ping(ip: string): Promise<boolean> {
  return new Promise((resolve) => {
    session.pingHost(ip, (error: Error) => {
      if (error) {
        return resolve(false);
      }

      resolve(true);
    });
  });
}