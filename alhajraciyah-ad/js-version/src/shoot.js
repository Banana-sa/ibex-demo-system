const { chromium } = require(process.env.PW || 'playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = [];
  p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + process.cwd() + '/alhajraciyah_ad.html');
  await p.evaluate(() => window.__ready);
  await p.screenshot({ path: 'qa_page.png' });
  const ts = process.argv.slice(2).map(Number);
  for (const t of ts) {
    const d = await p.evaluate(t => { window.__renderAt(t); return document.getElementById('cv').toDataURL('image/jpeg', .85); }, t);
    require('fs').writeFileSync(`qa_${t}.jpg`, Buffer.from(d.split(',')[1], 'base64'));
  }
  console.log('errors:', errs);
  await b.close();
})();
