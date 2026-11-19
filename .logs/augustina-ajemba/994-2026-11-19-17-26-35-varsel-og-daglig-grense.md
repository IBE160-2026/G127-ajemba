# Varsel og daglig grense

## 2026-11-19 kl. 17:26 — Augustina Ajemba

### Oppgave
Bygge story 2.3 (GitHub-issue #13) oppå opplastingen fra story 2.2: brukeren må bekrefte varselet om at tekst går til Google Gemini før første opplasting (FR-6), og hver bruker kan laste opp 5 PDF-er per dag (FR-7, SM-8). Reglene fra 2.2 gjelder fortsatt: PDF lagres ikke, midlertidige kopier slettes alltid, alt nytt er eiersopplåst med samme enhetlige 404.

### Plan
- Plan: `_bmad-output/initiative-recall/epic-upload-pdf-checks/story-upload-notice-acknowledgement-and-daily-limit-plan.md` (status `built`, risiko medium, rute full, implementert direkte uten kodeunderagent).
- Brukerens valg: 1A (varselet følger EXPERIENCE.md, ikke «alle lagrede sitater» fra AC 3 — begrunnelse i Plan Change Log), 2A (avkryssingen lagres med en gang, også når filen avvises), 3A (README-seksjonen skrives nå).
- Bare accepterte opplastinger teller. Dagen er lokal dato i `LIMIT_TIME_ZONE` (standard `Europe/Oslo`). Grensen er `UPLOADS_PER_DAY` (standard 5).

### Resultat
- Nytt: `lectures/notice.py` (varselteksten, `NOTICE_VERSION = 1`), `UploadLog` + migrasjon `0003_uploadlog.py`, `templates/lectures/_upload_notice.html`.
- Endret: `lectures/services.py` (varselsjekk først, grensesjekk + `UploadLog`-rad i samme `atomic()` som Lecture), `lectures/views.py`, `templates/lectures/upload.html`, `config/settings.py` (+ validering ved oppstart), `.env.example`, `README.md` (seksjon «AI notice and daily limit»), `docs/required_readme_headings.txt`, `lectures/tests.py`.
- Verifisert: `.venv/Scripts/python manage.py test` → 83 tester OK; `makemigrations --check` → ingen endringer. Matrisen er dekket av tester (fast klokke for midnatt, vinter- og sommertid).
- Ingen pakke installert (`tzdata` 2026.6 lå allerede inne). Testserver ble aldri startet, så ingen å stoppe. Ingenting er committet; loggfila er heller ikke committet (brukeren committer selv).
- Review 1: «quick»-linsen gjort av meg selv mot diffen (ingen reviewer-underagent, siden ingen ble bedt om); 0 funn beholdt.
- Review 2 (på brukerens forespørsel, reviewer-underagent mot hele diffen): UploadLog er eiersopplåst via `for_user` (ingen visning slår opp rader på id); 15 samtidige opplastinger med grense 5 ga nøyaktig 5 godtatt (midlertidig SQLite-fil, `db.sqlite3` urørt), ingen omgåelse. 6 funn triagert, se planens Review Triage Log. Rettet: fjernet ekstra overskrift «Before you upload» (aria-label i stedet), bare «Unpaid quota» er uthevet (som i EXPERIENCE.md, også i README), og testen `test_fr6_notice_text_matches_experience_md` sammenligner nå den gjengitte siden med EXPERIENCE.md (tekst og uthevinger; sjekket ved å sette de tre avvikene tilbake, testen feilet hver gang). Valg 1b A: den ekte lenken erstatter «(link)». Avvist: grensesjekk etter utpakking (AD-20-rekkefølge). Utsatt: bytte av `LIMIT_TIME_ZONE` på kjørende app (skrevet i `deferred-work.md`).
- Etter retting: 83 tester OK, `makemigrations --check` uten endringer. Ingenting committet.
- Avvik: planredigeringen ved godkjenning ble kjørt med systemets `python`, ikke `.venv/Scripts/python` (rørte bare plantekst).

### Åpne punkter
- Bytte av `LIMIT_TIME_ZONE` på en kjørende app kan slippe gjennom eller blokkere én opplasting (utsatt, se `deferred-work.md`).
- Manuell nettlesertest av varsel og avkryssing (ny bruker, med/uten avkryssing, 6. opplasting) gjenstår.
- Skissen sier at knappen er deaktivert til fil og avkryssing er valgt; det er ikke bygget (ingen JS, bare server-sjekk).
- Lagrede sitater som varselet utelater (f.eks. «Use Restrictions», «This includes disconnecting …») testes ikke; AC 3 er bevisst avvikt fra (se Plan Change Log). Oppdater AC 3/EXPERIENCE.md hvis kravteksten skal samsvare.
- epic-demo-readme skal bare sjekke README-kopien av varselet (den er laget i denne storyen).
- Test «sletting av forelesning senker ikke tellingen» finnes allerede her; epic-delete-report trenger bare å bruke den.
