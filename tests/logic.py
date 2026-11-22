# Test A: spellogik i alla lägen med en "bot" som styr via setPointer
import asyncio, json
from playwright.async_api import async_playwright
PAGE='file:///home/claude/boo-beats/index.html'
async def run_mode(b, mode, follow=True):
    ctx=await b.new_context(viewport={'width':390,'height':844}); pg=await ctx.new_page()
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(PAGE); await pg.wait_for_timeout(300)
    await pg.click(f'.mode[data-mode="{mode}"]')
    await pg.evaluate("document.getElementById('adv').open=true")
    await pg.select_option('#dur','45'); await pg.select_option('#bpm','120'); await pg.select_option('#step','2')
    await pg.click('#startBtn')
    centers=[1/6,.5,5/6]
    while True:
        st=await pg.evaluate("window.__bb.st()")
        if not st['running'] and st['T']==0 and await pg.is_visible('#result'): break
        n=st['next']
        if follow and n:
            # i besluts-lägen får boten bara agera när signalen visats (reveal)
            dec=n['kind'] in ('color','def')
            if (not dec) or st['T']>=n['t']-n['reveal']+0.05:
                await pg.evaluate(f"window.__bb.setPointer({centers[n['lane']]})")
        elif not follow:
            await pg.evaluate("window.__bb.setPointer(0.5)")
        await pg.wait_for_timeout(30)
    res=await pg.inner_text('#stats'); await ctx.close()
    return mode, res.replace('\n',' '), errs
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--autoplay-policy=no-user-gesture-required'])
        out=await asyncio.gather(*[run_mode(b,m) for m in ['slalom','pattern','color','def','mix']], run_mode(b,'slalom',follow=False))
        for o in out: print(o)
        await b.close()
asyncio.run(main())
