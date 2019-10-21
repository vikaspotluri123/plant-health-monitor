import execa from 'execa';

export default async function ping(ip: string): Promise<boolean> {
  try {
    const response = await execa.command(`ping ${ip} -n 1`);

    return response.stdout.split('\n')[2].indexOf(`Reply from ${ip}`) === 0;
  } catch (_) {
    return false;
  }
}