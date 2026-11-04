# Registrering, innlogging og utlogging

## 2026-11-04 kl. 14:00 — Augustina Ajemba

### Oppgave
Implementere story 1.2 (GitHub-issue #5) med bmad-build på grenen `story-1.2-register-login`: registrering, innlogging og utlogging med Djangos innebygde innlogging og e-postbrukeren fra story 1.1, grense på mislykket innlogging, trygg sjekk av `next`, websikkerhetsregler (AD-19), tømming av essay-sikkerhetskopien ved utlogging, og en «Accounts»-del i README. Brukeren er ny i Django og ville ha forklaring før hvert steg. Ingen commit.

### Plan
- Plan: [story-register-log-in-and-log-out-plan.md](../../_bmad-output/initiative-recall/epic-foundation-accounts/story-register-log-in-and-log-out-plan.md) (status `built`, risiko medium, rute full men bygget direkte uten underagent fordi brukeren ikke ba om agenter).
- Rekkefølge: finne htmx-kilde og få brukerens ja, plan, planvurdering (fem funn, fire rettet), innstillinger og middleware, login-grense og skjemaer, visninger og maler, `run.py`, README, tester, røyk-test av ekte server, selvgjennomgang.

### Resultat
- Nye filer: `accounts/{forms,views,urls,throttle}.py`, `config/middleware.py`, `templates/{base,lectures}.html`, `templates/accounts/{login,register}.html`, `static/vendor/htmx.min.js` og `htmx.SOURCE.txt`, `static/js/logout.js`, `static/css/recall.css`. Endret: `config/{settings,urls,views}.py`, `templates/home.html`, `run.py` (kjører `createcachetable`), `README.md` og `docs/required_readme_headings.txt` («Accounts»), `accounts/tests.py`, `config/tests.py`.
- htmx 2.0.10 kommer fra tag `v2.0.10` i `bigskysoftware/htmx` (`dist/htmx.min.js`). SHA-384 `sha384-H5SrcfygHmAuTDZphMHqBJLc3FhssKjG7w/CeCpFReSfwBWDTKpkzPP8c+cLsK+V` er lik hashen i README-en til samme tag. Kilde, versjon og hash ligger i `htmx.SOURCE.txt`, og en test sjekker dem.
- Valg: login-grensen er 5 feil per 15 min per e-post og adresse i en database-cache (`MAX_ENTRIES` 10000). Innloggingsskjemaet gjør e-posten til små bokstaver selv, siden brukermodellen ikke skulle endres. `/lectures/` er en enkel plassholder bak innlogging. htmx-innstillingene står i en `<meta>`-tagg (inkludert `includeIndicatorStyles:false`) fordi CSP forbyr inline script og stil.
- Tester: `python manage.py test` gir 28 tester OK uten `.env`; `check` og `makemigrations --check` er rene. Ekte server på port 8012: `/`, login, register, htmx, js og css ga 200, `/lectures/` ga 302 til login, CSP-headeren var til stede. Serveren ble stoppet og porten er lukket.
- Gjennomgang: selvgjennomgang av økta (ikke uavhengig), 0 høy, 0 medium, 2 lav. Ikke committet og ikke pushet.
- Underveis avviste brukeren en kommando (`pip download htmx` og `find /`): htmx er JavaScript og skal ikke komme fra PyPI, og søk skal holdes innenfor prosjektmappen. Fulgt.

### Åpne punkter
- Uavhengig kodegjennomgang av story 1.2 er ikke kjørt.
- Registrering har ingen grense på antall forsøk (bare innlogging har det).
- «Show password»-avkrysningen fra skissen er ikke bygget (ikke i kravene, trenger en statisk script-fil).
- `/lectures/` er en plassholder; story 1.3 og epic-summary gir den innhold.
- Telleren i login-grensen er ikke atomisk: to samtidige feil kan slippe gjennom ett ekstra forsøk. Akseptert for en lokal app.
- Statiske filer (htmx, CSS) serveres bare når `RECALL_ENV` er `local`; ved en annen verdi mangler styling og htmx til en statisk filserver (WhiteNoise) legges til.
- Selve tømmingen av `localStorage` ved utlogging kan bare sjekkes manuelt i nettleseren; brukeren kjører den manuelle testen.
