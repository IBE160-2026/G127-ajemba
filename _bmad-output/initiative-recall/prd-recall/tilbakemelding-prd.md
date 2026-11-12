# Tilbakemelding på PRD

| | |
|---|---|
| **Gruppe** | G127 – G127-ajemba |
| **PRD vurdert** | `_bmad-output/initiative-recall/prd-recall/prd-recall.md` (status `final`, sist endret 2026-11-03, commit ad6e2f1) |
| **Dato** | 2026-11-12 |
| **Type** | Formativ tilbakemelding, ikke karakter |

## 1. Samlet inntrykk

Dette er en sterk PRD med en klar tese (selvtesting for studenter på andrespråk, der hvert svar kan sjekkes mot lysbildene), testbare FR-er og en egen del om hvordan KI-ens svar kvalitetssikres. Risikoen ligger ikke i kvaliteten på kravene, men i at PRD-en beskriver mer enn tidsbudsjettet rommer: §8.1 sier at alt er med, mens §8.3 sier at kjernen alene er over budsjett. Dokumentet er også langt (ca. 9 600 ord), og endringshistorikken fyller mye.

## 2. Dette fungerer godt

- **Testbare krav med konkrete eksempler.** FR-15 har regler for stavevarianter og tre eksempeltester («"key" expected, "kay" rejected»), og FR-3, FR-4 og FR-7 har tallgrenser og «makes no AI call». Hvert FR kan bli en testsak nesten uendret.
- **Kvalitetssikring av KI er et eget fagstoff, ikke en bisetning.** §5 definerer hva «god output» er per type, fryser Reference Key Points før evaluering (FR-26), kalibrerer essaytilbakemelding med seks forhåndsmerkede svar per spørsmål, kjører hvert svar tre ganger (FR-29) og krever re-kjøring etter hver prompt-endring (FR-30). §5.7 sier ærlig hva sjekkene ikke beviser.
- **Ærlig avgrensning og personvern.** §7 og §8.2 er konkrete. §6.1 gjengir Googles vilkår for gratisnivået og sier hva det betyr (nøkkelen brukes bare lokalt, sensor bruker Demo Mode). SM-C1 til SM-C3 har egne «Reading»-linjer, så motmålene kan faktisk måles.

## 3. Oversikt per dimensjon

| Dimensjon | Vurdering | Kort begrunnelse |
|---|---|---|
| Beslutningsklarhet | sterk | Valg og avveininger er datert og begrunnet (§13–15), og åpne spørsmål 6, 9 og 10 er reelle. |
| Substans | sterk | Én persona som styrer designvalg, produktspesifikke NFR-er (WCAG, 60/120 s, Lighthouse ≥ 90). Ingen pynt. |
| Strategisk sammenheng | god | Tydelig tese og funksjoner som tjener den. Men tesen (lettere for andrespråk, 15 minutter) måles ikke (§5.7), og essay, kjernen i tesen, er «hvis tid». |
| Testbarhet | sterk | Tallfestede konsekvenser og eksempler. Noen krav ligger utenfor FR-ene (se 4.2). |
| Scope og avgrensning | god | Non-goals og «ute av v1» er tydelige. §8.1 og §8.3 motsier hverandre. |
| Brukbarhet for neste fase | god | Stabile ID-er, glossar og sporbarhetsregel (§6.5). FR-ene mangler prioritet, og historikken gjør dokumentet tungt å hente fra. |
| Formtilpasning | god | Passer et enkeltbrukerprodukt med én reise. Over-formalisert i §11–15. |

## 4. Viktigste forbedringer

### 4.1 Prioritet må stå på kravene, ikke bare i §8.3
- **Alvorlighet:** høy
- **Hvor:** §8.1 «Quizzes in three formats (FR-12 to FR-17)» mot §8.3 «The planning figure for the core is about 35 hours against about 30 available»
- **Problem og hvorfor det betyr noe:** §8.1 lister alle funksjoner som «in scope», mens §8.3 plasserer utfylling og essay (FR-14 til FR-17, FR-29) i «hvis tid», og kjernen er allerede 5 timer over budsjett. Vision, UJ-1 og tesen forutsetter alle tre testnivåer. Den som leser FR-ene alene, vet ikke hva som må bygges, og stories vil få feil rekkefølge. Hvis essay faller bort, mister PRD-en det som skiller Recall fra andre verktøy.
- **Forslag:** Legg en linje under hvert FR eller hver feature: `Priority: Core (epic 4)` eller `Priority: If time (epic 8)`. Endre §8.1 til to lister, «Core» og «If time». Skriv i Vision én setning om fallback: «If essays are dropped, v1 is summary plus multiple choice plus the slide-linked Review List.» Avgjør nå hva som kuttes dersom sjekkpunktet etter epic 3 viser mer enn 30 timer.

### 4.2 Krav som ligger utenfor FR-ene blir ikke til stories eller tester
- **Alvorlighet:** medium
- **Hvor:** §6.6 «Quiz progress … is kept when the student switches tab, reloads or leaves»; §6.3 tekststørrelse, Lighthouse ≥ 90, mobilbredde
- **Problem og hvorfor det betyr noe:** §6.5 krever at hver story og test nevner et FR, men disse kravene har ingen ID og ingen testbare konsekvenser. De havner utenfor sporbarheten.
- **Forslag:** Lag f.eks. `FR-32: Quiz progress is kept` med konsekvensene «After reload during question 5 of 10, the quiz opens at question 5 with earlier answers intact» og «For the Example Lecture, progress is lost when the browser session ends». Gjør tilsvarende for tekststørrelse (`FR-33`) og la Lighthouse-målet bli en SM.

### 4.3 Gjør faithfulness-målet målbart, og mål tesen minst én gang
- **Alvorlighet:** medium
- **Hvor:** §10 spørsmål 6 og 9; FR-28 «No unsupported statement in any Summary»
- **Problem og hvorfor det betyr noe:** «Unsupported» er ikke definert, og målet er binært, vurdert av én person. Det kan blokkere hver prompt-endring (FR-30). Tesen om andrespråk og «fifteen minutes» har ingen måling, så ingen SM viser om produktet løser det det lover.
- **Forslag:** Definer: «A statement is unsupported if none of the slides in its Source Reference says or directly implies it. Paraphrase counts as supported.» Legg til en fallback: «More than one unsupported statement per Summary fails; each one is logged.» Avtal én tidtaking av UJ-1 med en medstudent på andrespråk som `SM-12`, selv om utvalget er lite.

### 4.4 Svikt og grenser hos KI-tjenesten er bare delvis beskrevet
- **Alvorlighet:** medium
- **Hvor:** FR-5 «When the AI service is unreachable or returns unusable output»; FR-8 «under 60 seconds»
- **Problem og hvorfor det betyr noe:** Gratisnivået hos Gemini har kvoter, og et svar som «for mange kall» er en annen svikt enn «utilgjengelig». FR-8 sin tidsgrense avhenger av en ekstern tjeneste dere ikke styrer.
- **Forslag:** Legg til en konsekvens i FR-5: «If the AI service answers with a rate-limit error, the Lecture gets the status Failed with the message "The AI service is busy, try again in a minute" and a retry button. A test uses a stored rate-limit response.» Skriv i FR-8 hvordan tiden måles, f.eks. «median of three runs».

### 4.5 Flytt historikken og rydd i det som er utdatert
- **Alvorlighet:** medium
- **Hvor:** §11–15; §10 spørsmål 1–3; FR-26 «The number was reduced from three to five»
- **Problem og hvorfor det betyr noe:** Omtrent en femtedel av dokumentet er endringslogg. §10 spørsmål 1 sier at teknologi og AI-tjeneste ikke er valgt, mens §14 sier Gemini, og spørsmål 3 er allerede besvart. FR-26-setningen er feil (3 til 5 ble redusert til 2). Utdatert tekst gjør at arkitektur og stories kan hente feil opplysninger.
- **Forslag:** Flytt §11–15 til `prd-recall-changelog.md` og behold en lenke i §0. Fjern lukkede spørsmål fra §10. Skriv om spørsmål 1 og 2 til dagens status. Rett FR-26 til «reduced from three to five Test Lectures to two».

## 5. Mekaniske funn

- FR-1 til FR-31 og SM-1 til SM-11 er sammenhengende, og krysshenvisningene jeg sjekket løser seg. §12 sin gamle-til-ny-tabell og de eldre review-filene bruker utgåtte FR-numre, så ta bort eller merk tabellen tydelig.
- Ingen `[ASSUMPTION]`-tagger står igjen. §11 er en bekreftelseslogg og kan flyttes (4.5).
- Glossaret følges stort sett. Små avvik: «Test Lecture» (FR-26) mot «Test Set Lecture» (FR-29), og «example Lecture» mot «Example Lecture». «Reference Key Point» er definert to ganger i samme linje i glossaret.
- Kun UJ-1 finnes. Det passer for én persona, men feilløypa for Demo Mode (sensor) er ikke en reise, selv om FR-23 og FR-24 teller mye i vurderingen.

## 6. Før dere går videre

**Må avklares nå (før epics og stories):**
- Prioritet per FR og fallback hvis essay kuttes (4.1).
- Definisjon av «unsupported» (4.3), siden evalueringen i epic 6 avhenger av den.
- Krav utenfor FR-ene som skal inn i stories (4.2).

**Kan vente:** antall spørsmål (10/8/2), tegnterskelen i FR-4 og prosentmålene i FR-28. Alle er merket som startverdier med revisjonsvilkår.

**Oppfølging av briefen:** ja. Suksesskriteriene er gjort til testbare SM-er, kvalitetssikringen er et eget §5 med testsett og prompt-versjonering, navnet er «Recall», innlogging er avklart (FR-1, FR-2), primærbruker er valgt, og Demo Mode, `.env.example` og test-PDF er kommet inn (FR-23, FR-24).

## 7. Refleksjonsspørsmål

1. §11 sier at alle forutsetninger er «bekreftet» samme dag. Hvilke av dem endret dere fordi KI-forslaget ikke stemte med det dere ville, og hvordan sjekket dere de dere godtok uten endring?
2. Evalueringen i §5 bygger på at én person vurderer sammendragene. Hva gjør dere hvis KI-en og dere er uenige om hva som er «unsupported», og hvem avgjør?

_Vurdert mot kvalitetsrubrikken i bmad-prd. Dette er veiledning, ikke sensur._
