# Test D: menyflöde – kör pass klart, Kör igen, Avsluta, Meny, kameran flyttas rätt, inställningar dolda
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--autoplay-policy=no-user-gesture-required'])
        pg=await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.route('**/cdn.jsdelivr.net/**',lambda r:r.abort())
        await pg.goto('file:///home/claude/boo-beats/index.html')
        print('inställningar dolda:',not await pg.is_visible('#bpm'),'| version:',await pg.inner_text('.ver'))
        await pg.click('#camBtn'); await pg.wait_for_timeout(1000)
        print('kamera i menyn:',await pg.evaluate("document.getElementById('cam').parentElement.id"))
        await pg.evaluate("document.getElementById('adv').open=true"); await pg.select_option('#gate','0'); await pg.select_option('#dur','45')
        await pg.click('#startBtn'); await pg.wait_for_timeout(800)
        cls=await pg.evaluate("document.getElementById('cam').className"); print('under spel: kamera-klass',cls,'| meny dold',await pg.is_hidden('#menu'))
        await pg.click('#cam'); print('tryck på mini → tonad:',await pg.evaluate("document.getElementById('cam').classList.contains('off')"))
        await pg.click('#quit'); await pg.wait_for_timeout(400)
        print('Avsluta → resultat syns:',await pg.is_visible('#result'))
        await pg.click('#againBtn'); await pg.wait_for_timeout(800); print('Kör igen → spelar:',(await pg.evaluate("window.__bb.st()"))['running'])
        await pg.click('#quit'); await pg.wait_for_timeout(300); await pg.click('#menuBtn'); await pg.wait_for_timeout(300)
        print('Meny → meny syns:',await pg.is_visible('#menu'),'| kamera tillbaka i menyn:',await pg.evaluate("document.getElementById('cam').parentElement.id"))
        await pg.reload(); await pg.wait_for_timeout(1500)
        print('efter omladdning startar kameran själv:',await pg.is_visible('#camSlot'))
        print('fel:',errs); await b.close()
asyncio.run(main())
