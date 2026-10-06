# Tilbakemelding på product brief

| | |
|---|---|
| **Gruppe** | G127 – G127-ajemba |
| **Product brief** | `product-brief.md` (commit `69af85d`) |
| **Tilbakemelding fra** | Faglærer i IBE160 (utarbeidet med KI-støtte) |
| **Dato** | 2026-10-06 |

## Samlet vurdering

- **Bør revideres før dere går videre.** Rett punktene markert «Endre» før dere lager PRD og arkitektur.

Briefen er ellers godt skrevet. Det som må rettes er først og fremst suksesskriteriene, og det er en rask jobb.

**Det som er bra:**

1. Tydelig kjerneflyt: last opp → forstå → test. Problemet er konkret og godt begrunnet: tette lysbilder skrevet som talenotater, passiv gjenlesing som gir falsk trygghet, og forskning som viser at det virker å teste seg selv.
2. Tre testnivåer med en pedagogisk begrunnelse: flervalg for gjenkjenning, utfyllingsoppgaver for gjenkalling og essayspørsmål med tilbakemelding for forklaring. Tilbakemelding som peker tilbake til riktig del av forelesningen, gjør at studenten kan sjekke KI-en i stedet for å stole blindt på den.
3. Ærlig differensiering og tydelig avgrensning. Dere sier rett ut at Quizlet og NotebookLM finnes og at det ikke er noen teknisk vollgrav, og listen over hva som er ute av v1 (skannede PDF-er, lyd og video, spaced repetition, Canvas) er tydelig.

**De viktigste endringene:**

1. **Suksesskriteriene kan ikke måles i emnet.** «50 active student users», «40 % return within two weeks» og «cost of AI usage per user per month» krever en lansert tjeneste over et semester. Legg til funksjonelle kriterier som kan bli testtilfeller, for eksempel «en tekstbasert PDF på 30 sider gir et sammendrag på under 60 sekunder, og alle spørsmål har en henvisning til riktig del av sammendraget».
2. **Beskriv hvordan dere kontrollerer kvaliteten på KI-ens svar.** Det gjelder særlig tilbakemeldingen på essayspørsmål, der KI-en vurderer studentens svar. Bruk noen faste forelesninger der dere på forhånd skriver ned hovedpunktene, og sjekk at sammendrag, spørsmål og tilbakemeldinger stemmer med dem.
3. **Rydd opp i navn og lagring.** Tittelen sier «StudyLens», mens teksten sier «Recall». Velg ett navn. «A basic list of the student's uploaded lectures» betyr at materiale lagres. Avklar om det skal være innlogging, eller om appen kjører lokalt for én bruker uten konto.

## Vanskelighetsgrad og gjennomførbarhet

### Vurdert vanskelighetsgrad

- **Enkel**

**Sammenlignbart med:** 8) Foredragsnotater – sammendrag og quizgenerator (enkel) og 1) AI Study Buddy (enkel). Essayspørsmål med skriftlig tilbakemelding og henvisninger tilbake til kilden gjør at prosjektet ligger i den øvre delen av «enkel».

**Begrunnelse:**

| Faktor | Nivå (lav / middels / høy) | Kommentar |
|---|---|---|
| Domenelogikk – hvor mange og hvor kompliserte regler og beregninger må stemme? | lav | Poengberegning for flervalg og utfylling og en liste over emner å repetere. Retting av utfylling krever regler for stavevarianter. |
| Datamodell – antall entiteter og relasjoner mellom dem | lav | Forelesning, sammendrag med deler, spørsmål, forsøk, svar og rapporterte spørsmål. |
| Brukere, roller og innlogging | lav | Én rolle. Innlogging er ikke avklart, selv om forelesninger lagres. |
| KI-funksjonalitet i appen, f.eks. kall til språkmodell, prompts i koden og håndtering av usikre svar | middels | Sammendrag, tre spørsmålstyper og vurdering av essaysvar med henvisning til kilden. Vurderingen av fritekstsvar er den mest krevende delen. |
| Integrasjoner og eksterne tjenester, f.eks. API-er, betaling og e-post | lav | Ett LLM-API. |
| Sanntid, samtidighet eller flere brukere som påvirker hverandre | lav | Ingen. |
| Filhåndtering, f.eks. opplasting, PDF-lesing og eksport | middels | Opplasting og tekstuttrekk fra PDF. Lysbilder eksportert fra PowerPoint kan gi rotete tekst. Test tidlig med ekte lysbilder. |
| Sikkerhet og personvern | lav | Forelesningsmateriale og studentens svar sendes til en KI-tjeneste. Nevn dette, og hold opphavsrettsbeskyttet materiale utenfor repoet. |

**Hva vanskelighetsgraden betyr for dere:**

- _Enkel:_ Et enkelt prosjekt gir stor sjanse for å bli ferdig. Vanskelighetsgraden inngår likevel i vurderingen, så for å nå helt opp må dere vise mer i gjennomføringen. Det betyr særlig et gjennomarbeidet design, grundig testing, en tydelig dokumentert prosess og en README som virker. Grundig kvalitetssjekk av KI-svarene, særlig essaytilbakemeldingene, er en god måte å vise dette på.

### Gjennomførbarhet med BMAD og Claude Code

Dere skal planlegge med BMAD (product brief → PRD → arkitektur → epics og stories) og implementere med Claude Code. Vurderingen under tar hensyn til at det må være tid til hele denne flyten, og til testing, retting og README til slutt.

| Spørsmål | Vurdering (OK / risiko / stor risiko) | Kommentar |
|---|---|---|
| **Tid og omfang** – kan v1 realistisk bli ferdig og stabil i løpet av semesteret, med tid til flere iterasjoner? | OK | Seks funksjoner i én flyt er realistisk for én person, med tid til testing og forbedring. |
| **BMAD-flyten** – er briefen konkret nok til at PRD, arkitektur og stories kan lages uten store hull, og blir det overkommelig mange stories? | OK | Løsningen og scope er konkrete nok til en god PRD når suksesskriteriene er rettet. BMAD er ikke satt opp i repoet ennå. |
| **Egnet for Claude Code** – bruker løsningen en vanlig, godt dokumentert teknologistakk som Claude Code håndterer godt, eller krever den nisjeteknologi, spesialmaskinvare eller mye manuell konfigurasjon? | OK | En webapp med PDF-bibliotek og LLM-API er godt dokumentert. |
| **Kontroll på KI-ens arbeid** – kan gruppen selv avgjøre om koden gjør det riktige? Krever domenet kunnskap gruppen ikke har, f.eks. avanserte beregninger eller fagregler, så er det vanskelig å kvalitetssikre. | risiko | Dere kan vurdere sammendrag og spørsmål for forelesninger dere kjenner. Vurdering av essaysvar er vanskeligere å kontrollere og bør testes med kjente gode og dårlige svar. |
| **Testbarhet** – finnes det tydelige regler og forventede resultater som tester kan skrives mot? | risiko | Poengberegning, retting av utfylling, emneliste og rapportering kan testes. Suksesskriteriene i briefen er likevel ikke testbare i dag. |
| **Kjørbar for sensor** – kan appen kjøres lokalt etter README, uten gruppens nøkler, betalte kontoer eller egen infrastruktur? | risiko | Alle kjernefunksjoner krever LLM. Planlegg en demomodus med en ferdig behandlet eksempelforelesning, og beskriv i README hvordan sensor bruker egen nøkkel. |
| **Avhengigheter og kostnader** – krever løsningen betalte API-er, f.eks. språkmodeller, og finnes det en plan for kostnad, testmodus eller mock-data? | risiko | Kostnad er nevnt som forretningsmål, men det finnes ingen plan for testing. Lagre eksempelsvar, og sett en grense for PDF-størrelse. |

**Konklusjon om gjennomførbarhet:**

- **Gjennomførbart som beskrevet.**

**Forslag til justering av omfang eller vanskelighetsgrad:**

1. Behold v1, og skriv en prioritert «hvis tid»-liste. Spaced repetition eller en eksamensplan på tvers av flere forelesninger i samme emne er naturlige utvidelser som kan løfte vanskelighetsgraden.
2. Bygg i rekkefølgen sammendrag → flervalg → utfylling → essay med tilbakemelding, slik at dere har en fungerende app tidlig og kan bruke mest tid på den vanskeligste delen.

## Hvorfor product brief er viktig for mappen

Product brief er utgangspunktet for PRD, arkitektur, stories og til slutt koden. Del 1 av mappen vurderes blant annet på om sensor kan følge en sporbar vei fra plan til ferdig app. Den vurderes også på om appen gjør det dere har beskrevet, om den er testet, om den er godt designet, og om den kan kjøres etter README. Et uklart, for stort eller for lite brief gjør alt dette vanskeligere senere. Det er mye enklere å rette nå enn sent i semesteret.

## 1. Gjennomgang av briefens deler

| Del av brief | Status | Kommentar |
|---|---|---|
| Executive Summary – er det klart hva appen er, og hvilket problem den løser? | Juster | Svært tydelig, men navnet er ulikt i tittel (StudyLens) og tekst (Recall). |
| The Problem – er problemet konkret, med reelle situasjoner og brukere? | OK | Konkret med 30–60 sider per uke og fire beskrevne mestringsstrategier. |
| The Solution – beskriver løsningen brukeropplevelsen, ikke bare teknologi? | OK | Last opp → forstå → test er beskrevet fra studentens side, med resultat og emneliste etter hver quiz. |
| What Makes This Different – er vurderingen ærlig og realistisk? | OK | Ærlig og realistisk, med konkrete konkurrenter. |
| Who This Serves – er primærbrukerne tydelige, og vet vi hva de trenger? | Juster | To primærbrukere (travel student og student på andrespråk). Velg én for v1, eller forklar hva designet må gjøre for hver. |
| Success Criteria – kan kriteriene faktisk sjekkes eller testes? | Endre | Kriteriene er bruks- og forretningsmål som krever mange brukere over tid. Bare «under 60 sekunder» kan testes i emnet. |
| Scope – er det klart hva som er med i første versjon, og hva som ikke er det? | OK | Tydelig med og ute. Avklar bare innlogging når forelesninger lagres. |
| Vision – henger visjonen sammen med resten uten å blåse opp omfanget? | OK | Visjonen bygger videre på samme kjerne uten å påvirke v1. |

## 2. Utgangspunkt for del 1 av mappen

Punktene følger kriteriene i sensorveiledningen for del 1. Vektene i parentes viser hvor mye hvert kriterium teller i del 1.

| Kriterium i del 1 | Hva briefen bør legge til rette for | Status | Kommentar |
|---|---|---|---|
| **1. Prosess og KI-styring** (30 %) | Brief som er presis nok til at PRD og stories kan bygges direkte på den, slik at krav kan spores fra brief til kode. | Juster | Briefen er presis nok. Sett opp BMAD i repoet, flytt briefen til en planleggingsmappe, og lagre promptene for sammendrag, spørsmål og vurdering som versjonerte filer. |
| **2. Funksjonalitet og omfang** (20 %) | Realistisk omfang for gruppen og semesteret: en tydelig kjerneflyt som kan bli ferdig og stabil, og nok innhold til å vise reell funksjonalitet. | OK | Tydelig kjerneflyt med nok innhold. Tre spørsmålstyper gir mer å vise enn et minimum. |
| **3. Kvalitetssikring og testing** (15 %) | Suksesskriterier og funksjoner som er konkrete nok til å bli testtilfeller. | Endre | Erstatt forretningsmålene med funksjonelle kriterier, og lag et testsett med kjente forelesninger og eksempelsvar. |
| **4. Design og brukeropplevelse** (10 %) | Tydelige brukere og brukssituasjoner som designet kan bygges rundt, gjerne med de viktigste skjermbildene eller flytene skissert. | OK | Klar flyt og brukssituasjon. Skisser opplasting, sammendrag, quiz og resultatside. Husk tilgjengelighet, særlig for studenter på andrespråk. |
| **5. Kodekvalitet og arkitektur** (10 %) | Teknologivalg som er begrunnet og ikke mer komplekse enn appen trenger. | OK | Ingen teknologi er valgt ennå. Appen trenger ikke mer enn én webapp med enkel lagring. |
| **6. README og kjørbarhet** (10 %) | Løsning som andre kan kjøre lokalt uten betalte kontoer, og uten tilgang til gruppens egne tjenester og nøkler. | Juster | Planlegg `.env.example`, en demomodus med ferdig behandlet eksempelforelesning og en test-PDF i repoet. |
| **7. Ryddighet i repoet** (5 %) | En plan for hvor hemmeligheter, testdata og dokumentasjon skal ligge. | Juster | Bruk egne eller fritt tilgjengelige lysbilder som testdata, ikke opphavsrettsbeskyttet kursmateriell. Hold nøkler utenfor Git. |

## 3. Neste steg for gruppen

1. Skriv om suksesskriteriene til 5–8 funksjonelle kriterier som kan testes, og flytt bruks- og forretningsmålene til visjon.
2. Velg ett produktnavn, og avklar om lagrede forelesninger krever innlogging.
3. Sett opp BMAD i repoet og lag PRD med et eget avsnitt om hvordan KI-svarene kvalitetssikres.

Oppdater product brief i repoet når dere har gjort endringene, slik at historikken viser hvordan planen utviklet seg. Det er en del av prosessen sensor ser etter.
