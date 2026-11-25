# Sjekkpunkt 3.5: justert kutt

## 2026-11-25 kl. 15:26 — Augustina Ajemba

### Oppgave
Kjør bmad-build for story 3.5 «Checkpoint: compare real hours with estimates and adjust the cut» (issue #23). Beslutningen er brukerens, ingen app-kode skal endres. Skriv Decision-linja i initiative-Notes, og som egen oppgave: PRD-endringslogg, notat i evaluerings-epicet, README-seksjonen «What we checked and what we did not», og en CLAUDE.md-regel om at Claude aldri kjører git add/commit/push.

### Plan
- Plan (oneshot, kun dokumenter): `_bmad-output/initiative-recall/epic-summary/story-checkpoint-compare-real-hours-with-estimates-and-adjust-the-plan.md`.
- Brukerens kutt: epic 7 og 8 droppes (kun flervalg); milepæl 6 evaluerer kun `evaluation/testset/test-lecture-1.pdf`; epic 9 deretter 10 forblir «hvis tid».
- Review: ingen subagenter (ikke bedt om); egen gjennomgang av diffen. Commit-steget i bmad-build og i denne skillen hoppet over etter brukerens regel.

### Resultat
- `initiative-recall.md`: ny datert Decision-linje (2026-11-25) med timer brukt (~15 av 20), gjenstående (~16 + 2 + 2 + 8), frist 15. desember og de tre kuttpunktene.
- `prd-recall.md`: ny §16 «Changes from the checkpoint after epic 3 (2026-11-25)» for punkt 1 og 2.
- `epic-evaluation.md`: ny Decision i Notes om kun én testforelesning.
- `README.md`: nytt avsnitt om omfang (kun flervalg, én testforelesning), og «second deck comes later» rettet.
- `CLAUDE.md`: ny regel «Git: aldri add, commit eller push» som gjelder foran alle skills; sesjonslogg-avsnittet endret til at loggen ikke committes.
- Plan-fila flyttet til riktig sted i epic-summary (ticket `'5'`); `tickets.py next` viser ingen problemer.
- Test: `manage.py test` → 201 tester OK. Ingenting er committet.

### Åpne punkter
- `docs/time-log.md` (AC 1 og 2 i story 3.5) finnes ikke: brukeren ga bare totaltall (~15 t mot 20), ikke timer per story. Må fylles inn av brukeren.
- `tickets.toml` (AC 4) er ikke oppdatert for droppede epic 7 og 8; 8.x og 7.x står fortsatt som ventende, og 4.1 venter fortsatt på 3.5 til story 3.5 er markert ferdig.
- PRD sier fortsatt to testforelesninger og epic 7 og 8 i kuttet i §5.2/FR-26, SM-10 og §8.3 (kun endringsloggen §16 er oppdatert); epic-evaluation Done when/Description og stories 6.x nevner fortsatt to lectures.
- Avklar fristen: den opprinnelige Decision-linja sier slutten av november, ny er 15. desember (nevnt i den nye linja).

## 2026-11-25 kl. 15:32 — Augustina Ajemba

### Oppgave
Fullfør de fire åpne punktene i story 3.5: tidslogg, droppede epics i tickets.toml, evalueringsnotat, egen frist-Decision.

### Plan
- Samme plan som over; kun dokumenter, ingen git add/commit/push.

### Resultat
- Ny `docs/time-log.md` med timer per story (egne omtrentlige anslag, sum 15 t mot 20), gjenstående ~28 t, og kuttbeslutningen.
- Epic 7 og 8: `status: dropped` i epic-filene og `tier = "dropped"` i `tickets.toml`; `tickets.py next/status` gir ingen problemer.
- Evalueringsnotatet fantes fra før (ingen ny endring).
- Ny Decision-linje om fristen 15. desember i `initiative-recall.md`; den gamle linja er beholdt.
- Lukket i `issues.md`: time-log, tickets.toml, frist. Fullt testsett kjørt.

### Åpne punkter
- PRD §5.2/FR-26/SM-10/§8.3 og evalueringsepicets Description/Done when sier fortsatt to testforelesninger og epic 7–8 i kuttet (punktet står åpent i issues.md).
