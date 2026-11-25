# Bakgrunnsjobber, prosesseringsside og forelesningsliste

## 2026-11-25 kl. 10:13 — Augustina Ajemba

### Oppgave
Bygge story 3.2 (GitHub-issue #15) med bmad-build: en worker som kjører jobber bak `jobs.enqueue`, trygge statusendringer, prosesseringsside og «My lectures» med Processing/Ready/Failed, retry maks 3 ganger og AI-budsjett. Ingen AI-kall og ingen Gemini-nøkkel. PDF lagres ikke, alle nye tabeller og sider er eier-avgrenset med lik 404, README beskriver bare det appen gjør nå.

### Plan
- Plan: [story-background-jobs-processing-page-and-lecture-list-plan.md](../../_bmad-output/initiative-recall/epic-summary/story-background-jobs-processing-page-and-lecture-list-plan.md) (full rute, risiko høy, status `built`).
- Beslutninger fra brukeren: `AiCallLog` bygges her (variant A), eier-avgrenset, story 3.1 må skrive til den; hele planen beholdes uten splitt.
- django-q2 ble lest fra PyPI (read-only) og godkjent av brukeren før installasjon.

### Resultat
- Installert i `.venv`: django-q2 1.11.1 og django-picklefield 3.4.0 (begge MIT), festet i `requirements.txt`.
- Nytt/endret: `core/jobs.py` (eneste django_q-import, kun id-er), `set_status`/`reap_stale`/`retry_lecture`/`ai_budget_left` i `lectures/services.py`, modellen `AiCallLog` + migrasjon 0004, kommandoen `reap_stale`, status-adressen `/status/lecture/<id>/`, retry-adressen `/lectures/<id>/retry/`, maler (`_status`, `_status_row`, `detail`, `lectures`), `Q_CLUSTER` og nye innstillinger, `DATABASE_FILE`, README («How processing works», «If you deploy this»), `docs/django-q2-windows-test.md`.
- `run.py` starter nå web og worker sammen, stopper begge ved Ctrl+C/Ctrl+Break, og stopper den andre hvis den ene dør.
- Jobbkroppen er en stub som setter leksjonen til Failed (Summary kommer i story 3.3).
- django-q2 virker på Windows 11 / Python 3.13: tråd-fallback ble ikke bygget.
- Tester: hele suiten 105 OK (inkl. ny `lectures/test_processing.py` med ekte `qcluster`, og utvidede `RunPyStopsServerTests`). Ingen gjenværende server- eller worker-prosesser.
- Bivirkning: `migrate` og `reap_stale` ble kjørt mot den lokale `db.sqlite3`; 7 gamle fastlåste forelesninger ble satt til Failed.
- Ikke committet (brukeren committer selv etter gjennomgang), heller ikke denne loggen.

### Åpne punkter
- Uavhengig kodegjennomgang av story 3.2 er ikke kjørt (reviewer-underagent ikke bedt om); jeg leste diffen selv.
- Manuell test gjenstår: start `run.py`, last opp, lukk fanen, åpne listen, trykk Ctrl+C og sjekk at begge prosessene stopper.
- `logs/worker.log` (AD-15.2) er ikke laget; workeren logger bare til konsollen.
- Standardgrensene 30 (per bruker) og 200 (global) for AI-kall er mitt valg; bekreft eller endre.
- Story 3.1 må skrive én `AiCallLog`-rad per AI-kall, inkludert `local_day`.
- Story 3.3 må beholde `set_status` som første handling i den ekte Summary-jobben.

## 2026-11-25 kl. 10:16 — Augustina Ajemba

### Oppgave
Kjøre review-steget på hele diffen for story 3.2 med en reviewer-underagent (som i story 2.3), med fokus på: run.py-lekkasjer, dobbeltkjøring, eier-avgrenset 404, omgåelse av AI-budsjettet, slide-tekst i køtabeller og stale-markering. Vise funn og triage før endringer, deretter bruke godkjente rettelser.

### Plan
- Diff lagt i scratchpad (27 filer), én reviewer-underagent, alle seks fokuspunkt. Triage uten kodeendringer, så godkjenning fra brukeren: patch 1, 4 og 8, utsett 2 og 3, plus 9 og 10 slik brukeren bestemte.
- Triagen står i planens Review Triage Log; planfilen er den samme som over.

### Resultat
- 11 funn: 1 medium (latent), 6 low, 3 false, 1 planformulering. Ingen `intent_gap` eller `bad_plan`.
- Patch 1: `run.py` har nå `finally: stop_all(children)`; ny test `RunPyCleanUpTests`.
- Patch 4: `core/jobs.py` `run_job` logger bare klassenavnet og kaster `JobFailed(<klassenavn>) from None`, fordi django-q2 lagrer mislykkede oppgaver som `"{feil} : {traceback}"` og aldri sletter dem. Ny test sjekker at verken lagret tekst eller logg har slide-tekst (verifisert at testen feiler hvis feilen lenkes). Testkommentaren som lovte mer enn den sjekket er rettet.
- Patch 8: `_pid_alive` leser `tasklist /FO CSV` og sammenligner PID-kolonnen.
- Utsatt i `deferred-work.md`: story 3.3 må ha claim-steg eller generasjonsteller før ekte Summary-jobb (funn 3); SIGTERM på macOS/Linux (funn 2, med linje i README om kjente begrensninger); UX-gap for polish-epicen (funn 10).
- Funn 9 (`stop_server` → `stop_process`) som linje i Plan Change Log, uten å røre den frosne delen.
- Full suite: 107 tester OK. Ingen igjen-kjørende server- eller worker-prosesser. Ingenting committet.

### Åpne punkter
- Manuell test av `run.py` (opplasting, lukk fane, Ctrl+C) gjenstår.
- Se `deferred-work.md` for de tre utsatte punktene.

## 2026-11-25 kl. 10:55 — Augustina Ajemba

### Oppgave
Brukerens manuelle test av Ctrl+C i ekte terminal: alt stoppet og ingen python-prosesser ble igjen, men django-q2 skrev CRITICAL «reincarnated worker/monitor/pusher after sudden death» før stoppen. Spørsmål: kan workeren starte i egen prosessgruppe?

### Plan
- Les django-q2-kilden: Ctrl+C går til alle prosesser på konsollen; bare sentinelen ignorerer SIGINT, så pusher/monitor/worker dør og guarden starter dem på nytt.
- Egen prosessgruppe alene holder ikke (ingen ren stopp utenfra på Windows). Foreslått i stedet: barneprosessene ignorerer SIGINT (`multiprocessing.parent_process()`), med en test som sender ekte CTRL_C_EVENT. Test først, bevis at den feiler, så endre.
- Brukeren godkjente, men stoppet midt i og ba om fallback.

### Resultat
- Koden er uendret. Den halvferdige testen er fjernet igjen, så suiten er grønn.
- Testen kunne ikke reprodusere funnet: `run.py` avsluttet ikke etter Ctrl+C-hendelsen i den skjulte konsollen, og en prøvekjøring mot en database uten cache-tabellen ga bare `no such table: recall_cache`. Oppsettet må fikses (kjør `createcachetable`) før reproduksjonen blir troverdig.
- README fikk en linje under kjente begrensninger, `deferred-work.md` en oppføring (med forslag til rettelse), og planens Review Triage Log rad 12 («funnet ved brukerens manuelle test»).

### Åpne punkter
- Utsatt: Ctrl+C gir CRITICAL «reincarnated»-linjer i loggen (resultatet er riktig). Se `deferred-work.md`.

