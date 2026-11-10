const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1080, height: 1920 }, recordVideo: { dir: process.argv[2], size: { width: 1080, height: 1920 } } });
  const p = await ctx.newPage();
  await p.goto('file://' + process.cwd() + '/escena.html');
  await p.waitForTimeout(23000);
  await ctx.close(); await b.close();
})();
