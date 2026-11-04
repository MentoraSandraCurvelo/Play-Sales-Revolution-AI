const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + process.cwd() + '/frames.html');
  await p.waitForTimeout(500);
  const fs = await p.$$('.f');
  for (let i = 0; i < fs.length; i++) await fs[i].screenshot({ path: `f${i + 1}.png` });
  await b.close();
})();
