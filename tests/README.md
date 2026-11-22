# Automatiska tester för Boo Beats

Körs i en headless Chrome med Playwright.

- `logic.py` – alla fem lägen med en bot som följer portarna (ska ge 100 %), plus en bot som står still (~33 %).
- `genvid.py` – skapar en syntetisk kameravideo av en fotboll som rör sig nära och långt bort.
- `track.py` – låser bollen genom att trycka på den i kamerabilden och mäter att spårningen hamnar i rätt fil.
- `gate.py` – spelet startar först när bollen ligger i mitten, pausar när bollen tappas och fortsätter när den syns.
- `flow.py` – menyflödet: dolda inställningar, mini-kamera, Avsluta, Kör igen, Meny, kameran startar själv.
- `genfoot.py` + `foot.py` – en fot som rör sig bredvid och kliver över bollen; spårningen får inte hoppa till foten.
