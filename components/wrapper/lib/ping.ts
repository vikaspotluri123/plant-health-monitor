// @NOTE: we have to use CJS require here because the ping code is platform-dependent. The net-ping module
// has issues running on windows because the compiled binary doesn't load properly, which is why there's
// a require based on the platform.

import os from 'os';

const platform = os.platform();

let ping;
try {
  ping = require(`./ping/${platform}`).default;
} catch (_) {
  console.error(`Platform ${platform} is not supported`);
  process.exit(1);
}

export default ping as (ip: string) => Promise<boolean>;
