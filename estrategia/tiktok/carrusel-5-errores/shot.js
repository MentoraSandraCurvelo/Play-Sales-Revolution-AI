const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+__dirname+'/slides.html');await p.waitForTimeout(500);
const els=await p.$$('.s');for(let i=0;i<els.length;i++){await els[i].screenshot({path:__dirname+'/slide_'+(i+1)+'.png'});}
await b.close();})();
