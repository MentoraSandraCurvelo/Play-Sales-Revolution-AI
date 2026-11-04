const { chromium } = require('playwright');
const fsys = require('fs');
(async () => {
  let s = fsys.readFileSync('frames.html', 'utf8');
  s = s.replace('body{background:#000}', 'body{background:transparent}');
  s = s.replace('<div class="bg" style="background-image:url(bgnave.jpg)"></div>', '');
  fsys.writeFileSync('overlay.html', s);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + process.cwd() + '/overlay.html');
  await p.waitForTimeout(500);
  const fs = await p.$$('.f');
  await fs[0].screenshot({ path: 'o1.png', omitBackground: true });
  await b.close();
})();
