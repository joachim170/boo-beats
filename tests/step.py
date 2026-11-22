# Test H: spårning bild för bild (som på en snabb telefon: AI på varannan bild), exakt facit från videons json
import asyncio, os, sys, json
from playwright.async_api import async_playwright
REPO='/home/claude/boo-beats'; MP='/tmp/claude-0/mp/package'
name=sys.argv[1]; AIEVERY=int(sys.argv[2]) if len(sys.argv)>2 else 2; TAP=len(sys.argv)>3 and sys.argv[3]=='tap'
FR=f'/tmp/claude-0/vid/fr_{name}'; truth=json.load(open(f'/tmp/claude-0/vid/{name}.json'))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=await b.new_page(viewport={'width':390,'height':844})
        async def route(r):
            u=r.request.url
            if u.startswith('https://bb.local/fr/'): return await r.fulfill(path=os.path.join(FR,u.split('/')[-1]),content_type='image/jpeg')
            if u.startswith('https://bb.local/'):
                f=u[len('https://bb.local/'):].split('?')[0] or 'index.html'
                return await r.fulfill(path=os.path.join(REPO,f),content_type='text/html' if f.endswith('html') else 'application/octet-stream')
            if 'cdn.jsdelivr.net/npm/@mediapipe/tasks-vision' in u:
                f=u.split('@mediapipe/tasks-vision@')[1].split('/',1)[1]
                return await r.fulfill(path=os.path.join(MP,f),content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript',headers={'Access-Control-Allow-Origin':'*'})
            return await r.abort()
        await pg.route('**/*',route); await pg.goto('https://bb.local/index.html')
        await pg.evaluate("()=>{const c=document.createElement('canvas');c.width=640;c.height=480;window.__src=c;window.__bbTest.useCanvas(c);document.getElementById('trkMode').value='ai';}")
        await pg.evaluate("()=>{document.getElementById('trkMode').dispatchEvent(new Event('change'))}")
        for i in range(120):
            if await pg.evaluate("window.__bbTest.ready()"): break
            await pg.wait_for_timeout(500)
        print('ready',await pg.evaluate('window.__bbTest.ready()'),await pg.inner_text('#trkStatus'));
        n=min(int(os.environ.get('N','9999')),len(os.listdir(FR))); lane=lambda v:0 if v<1/3 else (1 if v<2/3 else 2)
        stats={'nära':[0,0,0],'långt':[0,0,0]}; line=''; firstLock=None
        START=int(os.environ.get('START','0'))
        for i in range(START,n):
            t=truth[min(i,len(truth)-1)]; tx_true=t[1]; r=t[3]
            res=await pg.evaluate('''async([url,ai,tap,tx,ty,__I])=>{const im=new Image();im.src=url;await im.decode();const c=window.__src;c.getContext('2d').drawImage(im,0,0);
               window.__bbTest.setClock(1000+tx*0+__I*66.7);const t0=1000+__I*66.7;
               if(tap){} 
               window.__bbTest.track(); if(ai) await window.__bbTest.aiStep();
               const s=window.__bbTest.state();return{tx:s.trackX,ok:s.lastSeen>=t0,tS:s.tS,tM:s.tMiss,tSc:s.tScore,ab:s.aiBox&&s.aiBox.score,tpx:s.tpos&&s.tpos.x/320,cOK:window.__bbTest.cok?window.__bbTest.cok():null}}''',[f'https://bb.local/fr/{i+1:04d}.jpg', i%AIEVERY==0, TAP and i==3, tx_true, t[2], i])
            if i<8 and os.environ.get('DBG'):
                bx=(1-tx_true)*640; print(i,'full-lower',await pg.evaluate('window.__bbTest.detect(0,144,640,336,0.05)'),'| full',await pg.evaluate('window.__bbTest.detect(0,0,640,480,0.05)'),'| zoom',await pg.evaluate(f'window.__bbTest.detect({bx-75},315,150,150,0.05)'))
            if os.environ.get('TR') and i<int(os.environ['TR']): print(i,round(tx_true,3),{k:(round(v,3) if isinstance(v,float) else v) for k,v in res.items() if k!='tp'}, res.get('tp') and (round(res['tp']['x']/320,3)))
            k='nära' if r>20 else 'långt'; st=stats[k]; st[0]+=1
            good=res['ok'] and res['tx'] is not None and lane(res['tx'])==lane(tx_true)
            if res['ok']: st[1]+=1
            if good: st[2]+=1
            if good and firstLock is None: firstLock=i
            line+=('#' if good else ('x' if res['ok'] else '.'))
        print(name,'AI var',AIEVERY,'bild','fel:',await pg.evaluate('window.__aiErr||null'))
        print(''.join(line[j] for j in range(0,len(line),2)))
        for k,(tot,trk,good) in stats.items(): print(f'  {k}: {tot} bilder, spårad {trk}, rätt fil {good} ({100*good//max(1,tot)} %)')
        print('  första låsning efter',firstLock,'bilder')
        await b.close()
asyncio.run(main())
