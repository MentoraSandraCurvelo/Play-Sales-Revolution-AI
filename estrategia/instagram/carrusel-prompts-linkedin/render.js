const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1080,height:1350}});
  await p.goto('file://' + process.cwd() + '/slides.html'); await p.waitForTimeout(500);
  for (let i = 1; i <= 6; i++) { await (await p.$('#s' + i)).screenshot({path: `slide${i}.png`}); }
  await b.close();
})();
