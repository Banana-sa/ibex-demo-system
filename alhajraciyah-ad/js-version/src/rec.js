const { chromium } = require(process.env.PW);
const { spawn } = require('child_process');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  await p.goto('file://' + process.cwd() + '/alhajraciyah_ad.html');
  await p.evaluate(() => window.__ready);
  const FPS = 30, N = Math.round(45 * FPS);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-r', String(FPS), '-i', '-', '-i', 'soundtrack3_norm.wav',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-maxrate', '8M', '-bufsize', '16M', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart',
    '-c:a', 'aac', '-b:a', '256k', '-shortest', 'alhajraciyah_ad_js.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < N; i++) {
    const d = await p.evaluate(t => { window.__renderAt(t); return document.getElementById('cv').toDataURL('image/jpeg', .95); }, i / FPS);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(i, '/', N);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  await b.close();
})();
