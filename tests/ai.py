# Test G: automatisk AI-spårning (utan att trycka) med realistisk boll, nära/långt, med/utan fot
import asyncio, os, sys, statistics
from playwright.async_api import async_playwright
REPO='/home/claude/boo-beats'; MP='/tmp/claude-0/mp/package'
VID=sys.argv[1]; SECS=float(sys.argv[2]) if len(sys.argv)>2 else 45
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream',f'--use-file-for-fake-video-capture={VID}','--enable-unsafe-swiftshader'])
        ctx=await b.new_context(viewport={'width':390,'height':844}); pg=await ctx.new_page()
        async def route(r):
            u=r.request.url
            if u.startswith('https://bb.local/'):
                f=u[len('https://bb.local/'):].split('?')[0] or 'index.html'
                ct={'html':'text/html','tflite':'application/octet-stream'}.get(f.split('.')[-1],'application/octet-stream')
                return await r.fulfill(path=os.path.join(REPO,f),content_type=ct)
            if 'cdn.jsdelivr.net/npm/@mediapipe/tasks-vision' in u:
                f=u.split('@mediapipe/tasks-vision@')[1].split('/',1)[1]
                ct='application/wasm' if f.endswith('.wasm') else 'application/javascript'
                return await r.fulfill(path=os.path.join(MP,f),content_type=ct,headers={'Access-Control-Allow-Origin':'*'})
            if 'cdn.jsdelivr.net' in u or 'googleapis' in u: return await r.abort()
            return await r.continue_()
        await pg.route('**/*',route)
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
        await pg.goto('https://bb.local/index.html'); await pg.click('#camBtn')
        for i in range(120):
            s=await pg.inner_text('#trkStatus')
            if 'AI-bilder/s' in s or 'gick inte' in s: break
            await pg.wait_for_timeout(500)
        print('status:',s, '| detektor:', await pg.evaluate("window.__bb.st().detector||''"))
        probe='''()=>{const c=document.getElementById('cam'),x=c.getContext('2d'),d=x.getImageData(0,0,240,180).data;let sx=0,n=0;
          for(let y=60;y<180;y++)for(let i=0;i<240;i++){const k=(y*240+i)*4,r=d[k],g=d[k+1],b=d[k+2],mx=Math.max(r,g,b),mn=Math.min(r,g,b);if(mn>165&&mx-mn<22){sx+=i;n++}}
          const st=window.__bb.st();return{ball:n>8?sx/n/240:null,n,tx:st.trackX,live:st.live,status:document.getElementById('trkStatus').textContent}}'''
        res=[]; t0=asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time()-t0<SECS:
            r=await pg.evaluate(probe); res.append(r); await pg.wait_for_timeout(200)
        import collections;print('n-värden:',sorted(r['n'] for r in res)[::max(1,len(res)//15)]);print('tidslinje:',''.join(('#' if r['live'] else '.') if r['ball'] is not None else ' ' for r in res));print('live totalt',sum(1 for r in res if r['live']),'/',len(res))
        lane=lambda v:0 if v<1/3 else (1 if v<2/3 else 2)
        for name,cond in [('nära',lambda r:r['n']>=50),('långt',lambda r:8<r['n']<50)]:
            rs=[r for r in res if r['ball'] is not None and cond(r)]
            live=[r for r in rs if r['live']]; okl=sum(1 for r in live if lane(r['tx'])==lane(r['ball']))
            print(f"{name}: {len(rs)} prover, följd {len(live)}, rätt fil {okl}/{len(rs)}")
        print('sista status:',res[-1]['status']); print('fel:',[e for e in errs if 'agent-proxy' not in e][:4])
        await pg.screenshot(path='/tmp/claude-0/tests/ai.png'); await b.close()
asyncio.run(main())
