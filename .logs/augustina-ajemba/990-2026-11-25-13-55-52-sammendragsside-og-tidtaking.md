# Sammendragsside og tidtaking

## 2026-11-25 kl. 13:55 — Augustina Ajemba

### Oppgave
Story 3.4 (issue #21): Summary-siden for en klar forelesning, med deler, kildehenvisninger, nøkkelbegreper og AI-merknad, etter wireframe 05, DESIGN.md/EXPERIENCE.md og WCAG-rettingene. Regler: kun eier ser siden (lik 404), AI-tekst alltid escapet, alle tester blokkerer ekte Gemini-kall. Den ekte tidtakingen er brukerens manuelle test.

### Plan
- Plan: [story-summary-page-and-a-real-timed-run-plan.md](../../_bmad-output/initiative-recall/epic-summary/story-summary-page-and-a-real-timed-run-plan.md) (godkjent, route full, risiko medium).
- Utelatt bevisst: quiz-/Results-faner, Text size, Demo-banner, Menu-knapp på telefon, hover-hjelp for begreper, «tilbake til spørsmålet», full restyling (epic-polish).
- Implementert direkte (ikke kodesubagent); reviewer-subagent (quick) kjørt etterpå.

### Resultat
- Ny side `/lectures/<id>/summary/` (`lecture_summary`, `get_summary`); `lecture_detail` sender Ready-forelesninger dit; `_status.html` får lenke «Open the summary» når polling ender på Ready.
- `format_slides()` i `core/text_utils.py`; delt `templates/_ai_notice.html`; `summary.html`, CSS (scoped `.summary`), `static/js/summary_focus.js` (fokus på del-overskrift, ingen inline script).
- `check_summary <id>` (SM-2, ingen AI) og `docs/summary-timing.md` (tom mal) + README-avsnitt (31–50 sider ikke tidtatt).
- Tester: `lectures/test_summary_page.py`, `core/test_format_slides.py`. Hele suiten: 192 OK, ingen ekte kall (0 Gemini-kall gjort av meg).
- Review (reviewer-subagent): 2 medium og tester rettet (manglende lenke fra Processing, `check_summary` OK uten deler); resten avvist eller notert i planens Review Triage Log. Ikke committet kode (planen sa det; brukeren committer selv).
- Ekte kjøring: 1 Gemini-kall normalt, maks 3 forsøk × 2 forespørsler = 6.

### Åpne punkter
- Brukerens manuelle tidtakte kjøring (start `run.py`, last opp egen testforelesning, mål tid) og utfylling av `docs/summary-timing.md`; deretter oppdatere README med resultatet (AC 6, 7, 8).
- AI-merknaden er en delt partial, ikke i `base.html` slik AC 3 bokstavelig sier; avklar om det holder.
- Story 3.4 er ikke committet (brukeren committer selv).

## 2026-11-25 kl. 14:34 — Augustina Ajemba

### Oppgave
Den manuelle tidtakingen (forelesning 13) fikk 503 to ganger på rad, og jobben feilet etter ett forsøk. Brukeren ba om flere forsøk med økende ventetid, innenfor jobbens tidsbudsjett, aldri ved «limit: 0».

### Plan
- Forslag og tester vist først; brukeren sa ja: 3 forsøk, 2/5/10 sekunder, grensen på 30 per bruker uendret.
- Funnet ført i planens Review Triage Log som funnet av brukerens manuelle test.

### Resultat
- `AI_RETRY_WAITS_S` (standard `2,5,10`, validert ved oppstart) erstatter `AI_RETRY_WAIT_S`; `call()` prøver 503/429 opptil 3 ganger, feiler med `job_budget` hvis ventetiden ikke får plass, og prøver aldri «limit: 0».
- Tester i `core/test_ai_client.py` og `lectures/test_summary_job.py` (fake transport, `_sleep` mocket, ingen ekte kall); README oppdatert.
- Reviewer-subagent kjørt på diffen; små rettinger gjort (budsjettgrense, loggilinje, test, README).
- Ingenting committet i denne runden (brukerens instruks: ikke commit noe, heller ikke loggen). Tidligere committet jeg én gang: `0ae7519 Logg: sammendragsside-og-tidtaking`.

### Åpne punkter
- Worst case er nå 12 forespørsler per opplasting, og hvert forsøk teller mot dagsgrensen på 30.
- Manuell tidtakt kjøring må gjentas (SM-1) og `docs/summary-timing.md` fylles ut.
- Gammelt `AI_RETRY_WAIT_S` i en `.env` ignoreres stille.
- Kode og logg for story 3.4 er ikke committet (brukeren committer selv).
