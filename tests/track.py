# Test B: AI-spårning med fejkad kamera (syntetisk fotboll) + modellen lokalt
import asyncio, json, os, statistics
from playwright.async_api import async_playwright
TF='/tmp/claude-0/tf/node_modules'; MODEL='/tmp/claude-0/m/package/models/coco-ssd'
PAGE='file:///home/claude/boo-beats/index.html'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--use-file-for-fake-video-capture=/tmp/claude-0/vid/ball.y4m','--autoplay-policy=no-user-gesture-required'])
        ctx=await b.new_context(viewport={'width':390,'height':844}); pg=await ctx.new_page()
        async def route(r):
            u=r.request.url
            if 'tf.min.js' in u: return await r.fulfill(path=TF+'/@tensorflow/tfjs/dist/tf.min.js',content_type='application/javascript')
            if 'coco-ssd.min.js' in u: return await r.fulfill(path=TF+'/@tensorflow-models/coco-ssd/dist/coco-ssd.min.js',content_type='application/javascript')
            if 'storage.googleapis.com' in u and os.environ.get('NOAI'): return await r.abort()
            if 'storage.googleapis.com' in u:
                f=u.split('/')[-1].split('?')[0]; return await r.fulfill(path=os.path.join(MODEL,f))
            return await r.continue_()
        await pg.route('**/*',route)
        logs=[]; pg.on('pageerror',lambda e:logs.append('ERR '+str(e)))
        await pg.goto(PAGE); await pg.wait_for_timeout(500)
        await pg.click('#camBtn')
        for i in range(120):
            s=await pg.inner_text('#trkStatus')
            if 'bilder/s' in s or 'redo' in s or 'inte' in s: break
            await pg.wait_for_timeout(500)
        print('status:',s)
        await pg.wait_for_timeout(800)
        pos=await pg.evaluate('''()=>{const c=document.getElementById('cam'),x=c.getContext('2d'),d=x.getImageData(0,0,240,180).data;let sx=0,sy=0,n=0;
          for(let y=70;y<180;y++)for(let i=0;i<240;i++){const k=(y*240+i)*4;if(d[k]>232&&d[k+1]>232&&d[k+2]>232&&!(d[k+2]>d[k]+4)){sx+=i;sy+=y;n++}}return n?[sx/n,sy/n]:null}''')
        box=await pg.locator('#cam').bounding_box()
        print('tap at',pos)
        await pg.mouse.click(box['x']+pos[0]/240*box['width'],box['y']+pos[1]/180*box['height'])
        # sampla: spårad x vs ”sanning” (vit boll-klump i kamerabilden, under ROI)
        js='''()=>{const c=document.getElementById('cam'),x=c.getContext('2d'),d=x.getImageData(0,0,240,180).data;let sx=0,n=0;
          for(let y=Math.floor(180*.3);y<180;y++)for(let i=0;i<240;i++){const k=(y*240+i)*4;if(d[k]>232&&d[k+1]>232&&d[k+2]>232&&!(d[k+2]>d[k]+4)){sx+=i;n++}}
          const st=window.__bb.st();return{truth:n>3?sx/n/240:null,n,tx:st.trackX,live:st.live,status:document.getElementById('trkStatus').textContent,seen:st.trackX!=null}}'''
        res=[]
        t0=asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time()-t0<50:
            r=await pg.evaluate(js); r['t']=asyncio.get_event_loop().time()-t0; res.append(r); await pg.wait_for_timeout(200)
        await pg.screenshot(path='/tmp/claude-0/tests/track.png')
        # klassa nära/långt via klumpstorlek (n pixlar)
        for name,cond in [('nära',lambda r:r['n']>=60),('långt',lambda r:3<r['n']<60)]:
            rs=[r for r in res if r['truth'] is not None and cond(r)]
            fresh=[r for r in rs if r.get('live')]
            errs=[abs(r['tx']-r['truth']) for r in fresh]
            lane=lambda x:0 if x<1/3 else (1 if x<2/3 else 2)
            lane_ok=sum(1 for r in fresh if lane(r['tx'])==lane(r['truth']))
            print(name,'prover',len(rs),'låst',len(fresh),'medelfel',round(statistics.mean(errs),3) if errs else None,'rätt fil',f"{lane_ok}/{len(rs)}")
        print('sista status:',res[-1]['status']); print(logs[:3])
        await b.close()
asyncio.run(main())
