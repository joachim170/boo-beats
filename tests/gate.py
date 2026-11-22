# Test C: start väntar på bollen i mitten, paus när bollen tappas, fortsätter när den syns
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--use-file-for-fake-video-capture=/tmp/claude-0/vid/ball.y4m','--autoplay-policy=no-user-gesture-required'])
        pg=await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/cdn.jsdelivr.net/**',lambda r:r.abort())
        await pg.goto('file:///home/claude/boo-beats/index.html'); await pg.click('.mode[data-mode="slalom"]'); await pg.click('#camBtn'); await pg.wait_for_timeout(2000)
        pos=await pg.evaluate('''()=>{const c=document.getElementById('cam'),x=c.getContext('2d'),d=x.getImageData(0,0,240,180).data;let sx=0,sy=0,n=0;
          for(let y=70;y<180;y++)for(let i=0;i<240;i++){const k=(y*240+i)*4;if(d[k]>232&&d[k+1]>232&&d[k+2]>232&&!(d[k+2]>d[k]+4)){sx+=i;sy+=y;n++}}return [sx/n,sy/n]}''')
        box=await pg.locator('#cam').bounding_box(); await pg.mouse.click(box['x']+pos[0]/240*box['width'],box['y']+pos[1]/180*box['height'])
        await pg.wait_for_timeout(500)
        await pg.click('#startBtn')
        st=await pg.evaluate("window.__bb.st()"); print('efter Spela: waiting',st['waiting'],'running',st['running'])
        for i in range(60):
            st=await pg.evaluate("window.__bb.st()")
            if st['running']: break
            await pg.wait_for_timeout(250)
        print('startade av bollen i mitten efter',i*0.25,'s → running',st['running'])
        await pg.wait_for_timeout(3000); t1=(await pg.evaluate("window.__bb.st()"))['T']
        # simulera tappad boll: byt till färgspårning utan låst färg
        await pg.evaluate("document.getElementById('trkMode').value='color';document.getElementById('trkMode').dispatchEvent(new Event('change'))")
        await pg.wait_for_timeout(2500); st=await pg.evaluate("window.__bb.st()"); ta=st['T']
        await pg.wait_for_timeout(1500); tb=(await pg.evaluate("window.__bb.st()"))['T']
        print('paus:',st['paused'],'ljud',st['acState'],'speltid står still:',round(tb-ta,2)==0)
        await pg.screenshot(path='/tmp/claude-0/tests/paused.png')
        await pg.evaluate("document.getElementById('trkMode').value='ai';document.getElementById('trkMode').dispatchEvent(new Event('change'))")
        await pg.wait_for_timeout(300)
        await pg.mouse.click(1,1)  # no-op
        # lås om bollen via mini-kameran går inte (mini = tona), så seeda via globalsökning: mallen finns kvar
        for i in range(40):
            st=await pg.evaluate("window.__bb.st()")
            if not st['paused']: break
            await pg.wait_for_timeout(250)
        print('fortsatte efter',i*0.25,'s → paused',st['paused'])
        print('fel:',errs)
        await b.close()
asyncio.run(main())
