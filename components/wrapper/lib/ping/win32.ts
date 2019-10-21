import execa from 'execa';
import {TIMEOUT} from './constants';

export default async function ping(ip: string): Promise<boolean> {
  try {
    const response = await execa.command(`ping ${ip} -n 1 -w ${TIMEOUT}`);

    return response.stdout.split('\n')[2].indexOf(`Reply from ${ip}`) === 0;
  } catch (_) {
    return false;
  }
}