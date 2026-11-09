const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + process.cwd() + '/cover.html'); await p.waitForTimeout(700);
  for (const i of [1,2]) await (await p.$('#c' + i)).screenshot({ path: `publicar/portada-opcion-${i}.jpg`, type:'jpeg', quality:92 });
  await b.close();
})();
