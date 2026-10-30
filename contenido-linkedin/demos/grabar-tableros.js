const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:1080,height:1350},deviceScaleFactor:1,recordVideo:{dir:'vid',size:{width:1080,height:1350}},colorScheme:'light'});
 const p=await ctx.newPage();
 await p.goto('file://'+process.cwd()+'/demo.html'); await p.waitForTimeout(1500);
 const w=t=>p.waitForTimeout(t);
 // Plan de Desarrollo (ciudadano)
 await p.click('#t-plan'); await w(2500);
 await p.mouse.wheel(0,500); await w(2500);
 await p.click('#pl-cite'); await w(2000);
 await p.click('#pl-ok'); await w(2000);
 await p.mouse.wheel(0,600); await w(3000);
 await p.screenshot({path:'plan-full.png',fullPage:true});
 await p.mouse.wheel(0,-2000); await w(800);
 // PQRSD
 await p.click('#t-pqrsd'); await w(2000);
 await p.mouse.wheel(0,350); await w(1200);
 for (const i of [1,4]){ await p.click(`#pq-table tbody tr:nth-child(${i+1})`); await w(2200);}
 await p.click('#pq-ok'); await w(1800);
 await p.mouse.wheel(0,-1000); await w(600);
 // SECOP
 await p.click('#t-secop'); await w(2000);
 await p.mouse.wheel(0,350); await w(1200);
 await p.click('#sc-table tbody tr:nth-child(5)'); await w(2500);
 await p.click('#sc-ok'); await w(2200);
 await p.mouse.wheel(0,-1000);await p.click('#t-plan'); await w(1500);
 await p.screenshot({path:'plan-top.png'});
 await ctx.close(); await b.close();
})();
