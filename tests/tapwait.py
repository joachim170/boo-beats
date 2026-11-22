# Test E: gammal inställning (färg) återställs till AI, och man kan låsa bollen på väntskärmen
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--use-file-for-fake-video-capture=/tmp/claude-0/vid/ball.y4m','--autoplay-policy=no-user-gesture-required'])
        ctx=await b.new_context(viewport={'width':390,'height':844})
        await ctx.add_init_script("try{localStorage.setItem('boobeats.trkMode','color');localStorage.setItem('boobeats.ver','0.6');localStorage.setItem('boobeats.camWanted','1')}catch(e){}")
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/cdn.jsdelivr.net/**',lambda r:r.abort())
        await pg.goto('file:///home/claude/boo-beats/index.html'); await pg.click('.mode[data-mode="slalom"]'); await pg.wait_for_timeout(2000)
        print('spårningsläge efter uppdatering:',await pg.input_value('#trkMode'))
        await ctx.add_init_script("")  # no-op
        await pg.click('#startBtn'); await pg.wait_for_timeout(600)
        print('stor kamera på väntskärmen:',await pg.evaluate("document.getElementById('cam').className"))
        await pg.screenshot(path='/tmp/claude-0/tests/wait07.png')
        pos=await pg.evaluate('''()=>{const c=document.getElementById('cam'),x=c.getContext('2d'),d=x.getImageData(0,0,240,180).data;let sx=0,sy=0,n=0;
          for(let y=70;y<180;y++)for(let i=0;i<240;i++){const k=(y*240+i)*4;if(d[k]>232&&d[k+1]>232&&d[k+2]>232&&!(d[k+2]>d[k]+4)){sx+=i;sy+=y;n++}}return [sx/n,sy/n]}''')
        box=await pg.locator('#cam').bounding_box(); await pg.mouse.click(box['x']+pos[0]/240*box['width'],box['y']+pos[1]/180*box['height'])
        for i in range(60):
            st=await pg.evaluate("window.__bb.st()")
            if st['running']: break
            await pg.wait_for_timeout(250)
        print('låst på väntskärmen → spelet startade:',st['running'],'efter',i*0.25,'s | kamera nu:',await pg.evaluate("document.getElementById('cam').className"))
        # spela 8 s och kolla att poäng rör sig (bollen följs)
        await pg.wait_for_timeout(8000); st=await pg.evaluate("window.__bb.st()"); print('efter 8 s: live',st['live'],'poäng',st['stats']['score'],'träff',st['stats']['hits'],'miss',st['stats']['miss'])
        print('fel:',errs); await b.close()
asyncio.run(main())
