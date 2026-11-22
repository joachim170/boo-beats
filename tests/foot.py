# Test F: foten får inte ”stjäla” spårningen
import asyncio, sys
from playwright.async_api import async_playwright
VID=sys.argv[1] if len(sys.argv)>1 else '/tmp/claude-0/vid/foot.y4m'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream',f'--use-file-for-fake-video-capture={VID}'])
        pg=await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/cdn.jsdelivr.net/**',lambda r:r.abort())
        await pg.goto('file:///home/claude/boo-beats/index.html'); await pg.click('#camBtn'); await pg.wait_for_timeout(1500)
        probe='''()=>{const c=document.getElementById('cam'),x=c.getContext('2d'),d=x.getImageData(0,0,240,180).data;let bx=0,bn=0,fx=0,fn=0;
          for(let y=70;y<180;y++)for(let i=0;i<240;i++){const k=(y*240+i)*4;if(d[k]>232&&d[k+1]>232&&d[k+2]>232&&!(d[k+2]>d[k]+4)){bx+=i;bn++}else if(d[k]<45&&d[k+1]<45&&d[k+2]<55&&d[k+3]){fx+=i;fn++}}
          const st=window.__bb.st();return{ball:bn>40?bx/bn/240:null,bn,foot:fn>30?fx/fn/240:null,tx:st.trackX,live:st.live}}'''
        # tryck på bollen när den syns tydligt
        for i in range(40):
            r=await pg.evaluate(probe)
            if r['ball'] and r['bn']>250: break
            await pg.wait_for_timeout(100)
        pos=await pg.evaluate('''()=>{const c=document.getElementById('cam'),x=c.getContext('2d'),d=x.getImageData(0,0,240,180).data;let sx=0,sy=0,n=0;
          for(let y=70;y<180;y++)for(let i=0;i<240;i++){const k=(y*240+i)*4;if(d[k]>232&&d[k+1]>232&&d[k+2]>232&&!(d[k+2]>d[k]+4)){sx+=i;sy+=y;n++}}return [sx/n,sy/n]}''')
        box=await pg.locator('#cam').bounding_box(); await pg.mouse.click(box['x']+pos[0]/240*box['width'],box['y']+pos[1]/180*box['height'])
        ok=onfoot=lost=0; vis=0; samples=0
        for i in range(200):
            await pg.wait_for_timeout(100); r=await pg.evaluate(probe); samples+=1
            if r['bn']>150: # bollen syns tydligt
                vis+=1
                if r['live'] and abs(r['tx']-r['ball'])<0.08: ok+=1
                elif r['live'] and r['foot'] is not None and abs(r['tx']-r['foot'])<abs(r['tx']-r['ball']): onfoot+=1
                elif not r['live']: lost+=1
            else: # bollen täckt: får inte vara ”live” på foten
                if r['live'] and r['foot'] is not None and r['ball'] is not None and abs(r['tx']-r['foot'])<0.05 and abs(r['tx']-r['ball'])>0.1: onfoot+=1
        print(f'bollen synlig {vis} prover: följde bollen {ok}, tappad {lost}, låste på foten {onfoot} (totalt)')
        print('fel:',errs); await b.close()
asyncio.run(main())
