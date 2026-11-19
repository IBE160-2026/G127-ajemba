# Last opp PDF med alle sjekker

## 2026-11-19 kl. 16:35 — Augustina Ajemba

### Oppgave
Bygge story 2.2 (GitHub-issue #11): opplasting av én PDF med sjekkene i fast rekkefølge (størrelse, `%PDF-`, utpakking i egen prosess med 20 s grense, sidetall, tekst per side). Gyldig fil blir en Lecture (`processing`) med én PageText per side. Brukeren ba om å bruke `core/pdf_text.py` med pypdf (ikke pdfplumber), ikke lagre PDF-en, eie-avgrense alle nye tabeller med lik 404, og fjerne alle midlertidige kopier i alle tilfeller.

### Plan
- Plan: [story-upload-a-pdf-with-all-checks-plan.md](../../_bmad-output/initiative-recall/epic-upload-pdf-checks/story-upload-a-pdf-with-all-checks-plan.md) (bmad-build, route full, risiko høy; implementert direkte, quick-review med én agent).
- `PageText` med `for_user`, tjenesten `create_lecture_from_upload`, side `/lectures/upload/`, README-seksjon «Upload limits».
- Ingen pakker installert. Ingen testserver startet. Ingen commit (brukeren committer selv).

### Resultat
- Nye/endrede filer: `lectures/models.py` (+ migrasjon 0002), `lectures/services.py`, `lectures/views.py`, `lectures/urls.py`, `lectures/upload_handlers.py`, `core/extract_cli.py`, `config/settings.py`, `templates/lectures/upload.html`, `templates/base.html`, README og `docs/required_readme_headings.txt`, `evaluation/make_test_fixtures.py` + `lectures/test_fixtures/encrypted.pdf`, tester i `lectures/tests.py`.
- Midlertidige filer: Djangos egen opplastingsfil og vår kopi slettes ved avvisning, tidsavbrudd og uventet feil; tester sjekker at mappen er tom etterpå.
- Review fant at Django lagret hele kroppen før 10 MB-sjekken; rettet med egen upload-handler. Svakere tester styrket.
- Verifisert: `.venv/Scripts/python manage.py test` → 62 tester OK; `makemigrations --check` uten endringer.
- Alt er ukommittert.

### Åpne punkter
- Minnegrense for utpakkingsprosessen (AD-20) er ikke implementert; kun 20 s grense. Ligger i `_bmad-output/initiative-recall/deferred-work.md`.
- Uavhengig kodegjennomgang av story 2.2 utover quick-lens er ikke kjørt.
- Manuell nettlesertest av opplastingssiden (gyldig og skannet PDF) er ikke gjort.
- Daglig grense og opplastingsvarsel kommer i story 3; i mellomtiden er det ingen grense.
