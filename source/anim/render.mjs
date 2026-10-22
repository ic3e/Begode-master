import { chromium } from 'playwright';
import fs from 'fs';
const [,,from='0',to='9999',step='1']=process.argv;
fs.mkdirSync('frames',{recursive:true});
const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1920,height:1080}});
p.on('console',m=>console.log('page:',m.text())); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('http://127.0.0.1:8765/index.html'); await p.waitForFunction('window.READY===true',null,{timeout:120000});
const n=await p.evaluate('window.NFRAMES'); const t0=Date.now();
for(let i=+from;i<Math.min(n,+to);i+=+step){ await p.evaluate(i=>window.setFrame(i),i);
  await p.screenshot({path:`frames/f${String(i).padStart(4,'0')}.png`}); if(i%30===0) console.log('frame',i,((Date.now()-t0)/1000).toFixed(1)+'s'); }
await b.close();
