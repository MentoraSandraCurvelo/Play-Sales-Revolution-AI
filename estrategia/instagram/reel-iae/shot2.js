const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + process.cwd() + '/cover.html'); await p.waitForTimeout(700);
  await (await p.$('#c2')).screenshot({ path: 'publicar/portada-opcion-2.jpg', type:'jpeg', quality:92 }); await b.close(); })();
