# Prosjektskjelett med e-postbruker og én-kommando-start

## 2026-10-29 kl. 22:35 — Augustina Ajemba

### Oppgave
Implementere story 1.1 (GitHub-issue #1) med bmad-build på grenen `story-1.1-project-skeleton`: Django 5.2 LTS-prosjekt med egen e-postbrukermodell før første migrering, settings kun i `settings.py`, og en `run.py` som virker på Windows. Brukeren er ny i Django og ville ha forklaring før hvert steg, og ville gjøre «din del» (venv og pakkeinstallasjon) selv. Ingen commit.

### Plan
- Plan: [story-project-skeleton-...-plan.md](../../_bmad-output/initiative-recall/epic-foundation-accounts/story-project-skeleton-with-email-user-model-and-one-command-start-plan.md) (status `built`, risiko medium, rute full men implementert direkte uten underagent).
- Rekkefølge: støttefiler, `accounts.User`, `config/settings.py`, `run.py`, README, tester, så brukeren laget `.venv` og installerte pakker, deretter første migrering, testkjøring og manuell sjekk.

### Resultat
- Nye filer: `requirements.txt` (Django 5.2.18, django-environ 0.14.0), `.env.example`, `.gitattributes`, `manage.py`, `config/` (settings, urls, views, wsgi, asgi, tests), `accounts/` (User, manager, tests, `migrations/0001_initial.py`), `templates/home.html`, `run.py`, `docs/required_readme_headings.txt`. Endret: `.gitignore` (db.sqlite3*, logs/), `README.md` ("Install and start", med PowerShell-notat om `Set-ExecutionPolicy -Scope Process` / `activate.bat` etter brukerens ønske).
- Migrering `accounts.0001_initial` laget etter at `AUTH_USER_MODEL` var satt; `makemigrations --check` rent.
- `python manage.py test`: 10 tester OK uten `.env` (12 etter Ctrl+C-rettelsen, se under).
- Manuelt verifisert av meg: `python run.py` uten `.env` ga HTTP 200 på `/`; simulert Python 3.11 ga melding om 3.12/3.13 og exit 1; `.env`, `db.sqlite3`, `logs/` ignoreres av git.
- Utført av brukeren: `python -m venv .venv` og `pip install -r requirements.txt` (første forsøk feilet fordi `!` kjører i Git Bash der `\` forsvinner; skråstrek løste det).
- Under testen ble en gjenværende `runserver`-prosess på port 8000 funnet og stoppet (venv-startprogrammet på Windows lager et ekstra prosesslag).
- Ikke committet etter brukerens instruks (arbeidsflyten hadde ellers gjort en lokal commit). Loggfila er heller ikke committet. Baseline: `c2745492392d921e93c11d066b0d038bf68f2cad`.
- **Feil funnet av brukerens manuelle test, ikke av selvgjennomgangen:** etter Ctrl+C i `python run.py` svarte siden på localhost:8000 fortsatt (bryter AD-15.1). Prosesslista viste `run.py` og serveren i live, i fire lag fordi hver `.venv\Scripts\python.exe` på Windows er et startprogram som starter den egentlige Python. Brukerens vurdering: `.venv`-startprogrammet var årsaken. Min verifisering: serveren blir værende hvis `run.py` forsvinner uten opprydding (beviset: to foreldreløse `runserver`-prosesser, siden ga 200), og den gamle `subprocess.call`-ventingen kan ikke vekkes av Ctrl+C på Windows. Et rent Ctrl+C alene lot seg ikke gjenskape i fire testvarianter (vanlig, tomme forbindelser, halv forespørsel, keep-alive), så den eksakte utløseren er ikke bevist. Første gjenskapingsforsøk var feil oppsatt (arvet «ignorer Ctrl+C» fra testprogrammet) og ble forkastet.
- **Rettelse i `run.py`:** venter i runder på 0,2 s; ved Ctrl+C/Ctrl+Break får serveren 3 s, deretter `taskkill /F /T`; Windows jobbobjekt (`KILL_ON_JOB_CLOSE`) dreper alle barneprosesser når `run.py` slutter, også ved krasj eller drept prosess; nytt `--port`. To nye Windows-tester i `config/tests.py` (`test_server_dies_when_run_py_is_killed`, `test_ctrl_break_stops_run_py_and_server`). Hele pakken: 12 tester OK. Brukeren gjentok den manuelle nettlesertesten etter rettelsen: Firefox får ikke kontakt med localhost:8000 etter Ctrl+C.
- Plan oppdatert: funn og rettelse i triage-loggen, og en manuell Ctrl+C-sjekk lagt til i Verification. Ikke committet.
- Avgjort: django-q2 og WhiteNoise utsatt til de trengs; ingen `django.contrib.admin`; `notice_ack_at`/`notice_version` lagt på User nå (AD-7/AD-17).

### Åpne punkter
- Ingen uavhengig kodegjennomgang er kjørt (kun selvgjennomgang i planens triage-logg). Kjør `bmad-review` eller `/code-review` før merge hvis det kreves.
- `bulk_create` på User omgår e-postnormaliseringen i `save()`; ingen slik kode finnes nå, men vær oppmerksom i senere stories (seeding, testdata).
- Testen «start med kopiert `.env.example` og fiendtlig miljøvariabel» (AD-12.2) hører til nøkkel-historien i epic-summary, ikke gjort her.
