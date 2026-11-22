# Test I: Boo Run – laddar 3D, startar, en bot styr (filbyte + hopp), skärmdumpar, inga fel
import asyncio, os, sys
from playwright.async_api import async_playwright
REPO='/home/claude/boo-beats'; THREE='/tmp/claude-0/three/package/build/three.min.js'
SECS=float(sys.argv[1]) if len(sys.argv)>1 else 40; BOT=(sys.argv[2] if len(sys.argv)>2 else 'smart')
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--autoplay-policy=no-user-gesture-required','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
        pg=await b.new_page(viewport={'width':390,'height':844}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
        async def route(r):
            u=r.request.url
            if 'three.min.js' in u: return await r.fulfill(path=THREE,content_type='application/javascript')
            if u.startswith('https://bb.local/'):
                f=u[len('https://bb.local/'):].split('?')[0] or 'index.html'
                return await r.fulfill(path=os.path.join(REPO,f),content_type='text/html' if f.endswith('html') else 'application/javascript')
            return await r.abort()
        await pg.route('**/*',route); await pg.goto('https://bb.local/index.html'); await pg.wait_for_timeout(500)
        await pg.screenshot(path='/tmp/claude-0/tests/run_menu.png')
        await pg.click('.mode[data-mode="run"]'); await pg.click('#startBtn'); await pg.wait_for_timeout(1500)
        await pg.screenshot(path='/tmp/claude-0/tests/run_count.png')
        await pg.wait_for_timeout(2500)
        centers=[1/6,.5,5/6]; shots=0; t0=asyncio.get_event_loop().time(); jumps=0
        while asyncio.get_event_loop().time()-t0<SECS:
            st=await pg.evaluate("({r:BooRun.state,o:BooRun.peek(),running:window.__bb.st().running})")
            if not st['running']: break
            if BOT=='smart':
                obs=[o for o in st['o'] if o['z']>-14 and o['z']<0.5]
                block={0:False,1:False,2:False}; low={0:False,1:False,2:False}; can=None
                for o in obs:
                    if o['type'] in('cart',): block[o['lane']]=True
                    if o['type'] in('tackle','low'): low[o['lane']]=True
                    if o['type']=='wall': low={0:True,1:True,2:True}
                    if o['type']=='caneta': can=o['lane']
                cur=st['r']['lane']
                if can is not None and not block[can]: tgt=can
                elif block[cur] or (low[cur] and not st['r']['jumpEnabled']): tgt=min([l for l in (0,1,2) if not block[l]] or [cur],key=lambda l:abs(l-cur))
                else: tgt=cur
                await pg.evaluate(f"window.__bb.setPointer({centers[tgt]})")
                if any(o['type'] in('tackle','low','wall') and (o['type']=='wall' or o['lane']==tgt) and -3.2<o['z']<-1.8 for o in obs):
                    await pg.keyboard.press('ArrowUp'); jumps+=1
            if shots<3 and asyncio.get_event_loop().time()-t0>4+shots*6:
                await pg.screenshot(path=f'/tmp/claude-0/tests/run_play{shots}.png'); shots+=1
            await pg.wait_for_timeout(60)
        r=await pg.evaluate("BooRun.state")
        print(f"bot={BOT}: sträcka {round(r['dist'])} m, poäng {r['score']}, mynt {r['coins']}, canetas {r['canetas']}, chapéus {r['chapeus']}, gol {r['gols']}, liv kvar {r['lives']}, hopp tryckta {jumps}")
        await pg.wait_for_timeout(1500); print('resultat syns:',await pg.is_visible('#result'))
        print('fel:',[e for e in errs if 'net::' not in e][:5]); await b.close()
asyncio.run(main())
