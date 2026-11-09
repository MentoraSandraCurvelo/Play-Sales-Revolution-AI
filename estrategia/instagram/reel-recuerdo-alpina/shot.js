const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + process.cwd() + '/overlays.html');
  await p.waitForTimeout(600);
  for (let i = 1; i <= 5; i++) await (await p.$('#o' + i)).screenshot({ path: `o${i}.png`, omitBackground: true });
  await b.close();
})();
