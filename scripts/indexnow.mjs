// Tell IndexNow search engines (Bing, Yandex, Seznam, Naver; Bing also feeds
// ChatGPT search and Copilot) that the site's pages changed. Run after a deploy:
//   node scripts/indexnow.mjs            submit every URL in public/sitemap.xml
//   node scripts/indexnow.mjs /pricing   submit only the given paths
// The key is public by design; the engine checks it at https://tryproperpdf.app/<key>.txt.
import { readFileSync, readdirSync } from 'node:fs';

const host = 'tryproperpdf.app';
const keyFile = readdirSync('public').find(name => /^[0-9a-f]{32}\.txt$/.test(name));
if (!keyFile) throw new Error('IndexNow key file missing from public/. Run `npm run build` first.');
const key = keyFile.slice(0, -4);

const args = process.argv.slice(2);
const urlList = args.length
  ? args.map(path => `https://${host}${path.startsWith('/') ? path : `/${path}`}`)
  : [...readFileSync('public/sitemap.xml', 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => match[1]);

const response = await fetch('https://api.indexnow.org/indexnow', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json; charset=utf-8' },
  body: JSON.stringify({ host, key, keyLocation: `https://${host}/${keyFile}`, urlList }),
});
// 200 = accepted, 202 = accepted and the key is still being validated.
console.log(`IndexNow: HTTP ${response.status} for ${urlList.length} URL(s)`);
if (!response.ok) process.exitCode = 1;
