const {chromium}=require('playwright');
(async()=>{
 const out=process.argv[2];
 const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:1080,height:1350},recordVideo:{dir:out,size:{width:1080,height:1350}}});
 const p=await ctx.newPage();
 await p.goto('file://'+__dirname+'/video-juridico.html',{waitUntil:'networkidle'});
 await p.evaluate(()=>document.fonts.ready);
 await p.evaluate(()=>window.run());
 await p.waitForFunction(()=>window.done,null,{timeout:120000});
 await ctx.close(); await b.close();
})();
