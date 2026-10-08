Promptlogg 6. oktober 2026: product brief, BMAD-oppsett og PRD

Denne loggen viser promptene jeg sendte til Claude Code 6. oktober 2026, i rekkefølge, med hva som skjedde og hvor jeg korrigerte KI-en. Den hører sammen med commit-historikken og BMAD-loggene (.memlog.md) i _bmad-output/initiative-recall/.

Kontekst og åpenhet om KI-bruk
Claude Code (modell: Sonnet 5.5, Claude Pro) ble brukt i terminalen i VS Code for BMAD-oppsett, gjennomgang av product brief og PRD.
Claude (claude.ai) ble brukt som veileder underveis: til å lære Git, VS Code og terminalen, til å skrive første utkast av product brief, og til å formulere flere av promptene under. Jeg har lest, vurdert og tilpasset promptene før jeg sendte dem, og tatt beslutningene selv.
Claude Code kjørte i manuell modus: hver kommando og filendring måtte godkjennes av meg før den ble utført. Der jeg sa nei, står det under.
Viktige valg før og under oppsettet
Valg	Hva jeg valgte	Begrunnelse
Endringer etter tilbakemelding på brief	Ett commit per tilbakemeldingspunkt	Gjør det mulig å følge hvordan briefen utviklet seg
BMAD-installasjon	Installert i prosjektet (ikke globalt)	Faglærer ba om at BMAD settes opp i repoet
Installasjonsmetode	Kopi i stedet for symlenker	Symlenker fungerer dårlig på Windows og i OneDrive, og kan brytes når andre kloner repoet
Modell	Byttet fra Opus til Sonnet	Sonnet holder til planleggingsarbeid og bruker mindre av kvoten
Modus	Manuell modus (ikke auto)	Jeg ville se og godkjenne hver endring selv
PRD-arbeidsmåte	"Fast path" med merkede antakelser	Briefen var allerede detaljert; antakelsene skulle bekreftes eller rettes av meg
Flytting av brief	git mv	Bevarer historikken til filen etter flytting
Økt 1: BMAD-oppsett og gjennomgang av product brief
Prompt 1: Oppsett av BMAD
Run bmad setup

Resultat: BMAD ble satt opp med modulene core-tools og method (versjon 6.13.0-next). Ingen spørsmål å besvare. Jeg committet oppsettet selv etterpå ("Set up BMAD").

Prompt 2: Gjennomgang av briefen mot tilbakemeldingen (kun lesing)
Use bmad-product-brief to review product-brief.md against the lecturer's feedback in tilbakemelding-product-brief.md. First tell me which feedback points are fully addressed and which are not. Don't change any files yet. Also tell me where BMAD expects the product brief to be stored.

Hvorfor slik: Jeg ba om en vurdering før endringer, slik at jeg kunne ta stilling til funnene selv.

Resultat: Hovedpunktene fra faglærer (testbare suksesskriterier, kvalitetssikring av KI-svar, ett navn, innlogging) var løst. KI-en fant i tillegg tre kriterier som ikke var presise nok til å testes, og noen formateringsfeil. Briefen lå utenfor BMAD-strukturen.

Prompt 3: Oppdatering med mine beslutninger
Yes, go ahead with the update, with these decisions:
- PDF size limit: maximum 50 pages and 10 MB.
- Fill-in-the-gaps: one wrong letter is accepted only for words of 5 letters or more. Shorter words must be exact. Case and extra spaces are always ignored.
- Essay feedback passes when, in all test lectures, every known good answer is rated above every known weak answer.
Use git mv when moving the brief so the file history is kept. Keep the tilbakemelding file where it is. Do not commit. When you're done, show me a summary of what changed.

Hvorfor slik: KI-en foreslo å "stramme inn" tre kriterier, men verdiene måtte være mine beslutninger, ikke KI-ens. Jeg ba også om at ingenting ble committet, slik at jeg kunne kontrollere resultatet først.

Resultat: Briefen ble flyttet til _bmad-output/initiative-recall/brief-recall/brief-recall.md med git mv, kriteriene fikk mine verdier, og beslutningene ble logget i .memlog.md. Jeg kontrollerte filen i forhåndsvisning og committet selv.

Økt 2: PRD
Prompt 4: Start av PRD
Run bmad-prd for the Recall initiative, using the product brief in _bmad-output/initiative-recall/brief-recall/brief-recall.md and the lecturer's feedback in tilbakemelding-product-brief.md as input. The PRD must include a dedicated section on how the quality of the AI's output is checked, as the lecturer asked. Ask me questions one at a time, and wait for my answer before moving on. Do not commit anything.

Hvorfor slik: Faglærer ba om et eget avsnitt om kvalitetssikring av KI-svar. "Ett spørsmål om gangen" sikret at det var mine svar, ikke KI-ens gjetninger, som formet dokumentet.

Prompt 5: Kontekst utover briefen
A few things beyond the brief:
- Team size: I'm working alone (group G127 has one member).
- Tech stack and LLM: not decided yet. That belongs in the architecture step. Keep it simple: one web app with simple storage, as the lecturer suggested.
- Language: the documents are in English. The app's interface language for v1 should be English.
- Test lectures: none chosen yet. I will use my own or freely licensed slides, never copyrighted course material.
- Grading: the lecturer's feedback lists the criteria. The app must run locally from the README without my keys or paid accounts (demo mode, .env.example, a test PDF in the repo), and testing, design and a documented process count heavily. The project is rated "simple", so thorough testing and quality checks of the AI output are how to show more.
- Deadline: [ Deadline: not known yet.]
Prompt 6: Ambisjonsnivå
Yes Graded course project
Prompt 7: Arbeidsmåte
Fast path. Mark every assumption clearly, and list all of them at the end of your reply so I can confirm or correct each one.

Hvorfor slik: Raskere enn å gå gjennom hver seksjon, men alle antakelser skulle merkes og kontrolleres av meg.

Prompt 8: Brukerreisen
Amara is an international student at Høgskolen i Molde, studying IT and digitalisation in English, which is her second language. On Tuesday she had a lecture in her databases course on normalisation, with 40 slides.

That evening she logs in to Recall and uploads the lecture PDF. Within a minute she sees a plain-language summary split into short parts, each showing which slides it comes from. Below it is a list of key terms like "functional dependency" and "third normal form", each with a short, simple explanation.

She reads the summary in about five minutes, then starts a quiz. She does multiple choice first and gets 7 of 10. Then fill-in-the-gaps, where she types the key terms herself. Finally she answers one essay question: "Explain why we normalise a database." She writes a short answer in her own words. The feedback tells her she explained redundancy well but missed update anomalies, and links to the part of the summary about that, from slides 12 to 15.

On the results page she sees her score and a review list with two topics: update anomalies and third normal form. She clicks the first one, which takes her back to that part of the summary, rereads it, and opens slides 12 to 15 in her own copy.

The lecture and her results are saved to her account, so she can come back to them before the exam. The whole session takes about 15 minutes.

Resultat: Første utkast av PRD med 29 merkede antakelser.

Prompt 9: Bekreftelse av antakelser, med én endring

Jeg gikk gjennom alle 29 antakelsene. Under gjennomgangen fant jeg at ett suksessmål ikke var målbart: "no unsupported statements in most Summaries". Jeg bekreftet de øvrige antakelsene og ba om at målet ble gjort målbart. Endelig formulering: "no unsupported statement in any Summary in the Test Set".

Der jeg avviste eller korrigerte KI-en
Korreksjon 1: KI-en ville slette listen over antakelser

Claude Code foreslo en kommando som ville erstatte hele avsnitt 11 (listen over antakelser) med ett kort avsnitt, og som brukte feil formulering av målet over. Jeg svarte nei og sendte:

Two corrections before you continue:
1. I asked for "no unsupported statements in any Summary in the Test Set", not "all but at most one". Make sure FR-25, SM-9 and section 11 use my wording.
2. Keep the full list of assumptions in section 11. Rename it "Confirmed Assumptions", keep every item, and mark each as confirmed on 2026-10-06, with the FR-25/SM-9 change noted. A reader should be able to see what was assumed and that I confirmed it.

Hvorfor: Listen dokumenterer hva KI-en antok og at jeg kontrollerte det. Å slette den ville fjernet sporet av kvalitetssikringen.

Korreksjon 2: Feil i beslutningsloggen

KI-en ville logge at jeg hadde bedt om formuleringen "all but at most one Test Lecture", og at det var 27 antakelser (listen hadde 29). Jeg svarte nei og sendte:

Please correct the memlog entries before running them:
1. The wording "all but at most one Test Lecture" was introduced by you (Claude), not by me. I asked for "any Summary in the Test Set" from the start, and corrected your wording. Log it that way.
2. Count the items in section 11 and use the actual number instead of 27.
Then run the logging and git status.

Antallet ble rettet, men loggteksten tilskrev fortsatt formuleringen til meg. Jeg svarte nei igjen, og ba om en nøytral formulering:

Make the second entry neutral instead: "FR-25 and SM-9 faithfulness target: the draft said 'no unsupported statements in most Summaries', which is not measurable. An intermediate wording, 'all but at most one Test Lecture', was briefly used and then replaced. Final wording, confirmed by the builder: 'no unsupported statement in any Summary in the Test Set'." Then run the logging and git status.

Hvorfor: En beslutningslogg er bare nyttig hvis den viser riktig hvem som bestemte hva.

Avslutning av PRD
Prompt 10: Gjennomgang før endringer
Yes, go ahead with the finalize steps. Show me the reviewer's findings before changing anything, and do not commit.

Resultat: Tre gjennomganger (rubrikk, sammenligning med brief, sammenligning med faglærers tilbakemelding). Ingen kritiske funn, 2 høye, 5 middels og 10 lave.

Prompt 11: Hvilke funn som skulle rettes
Fix these: High 1 (freeze essay questions and key points for test lectures in the repo), High 2 (change Amara's lecture to 30 slides), Medium 3 (builder checks the marked correct answers in the Test Set), all low and mechanical fixes, brief gap 1 (plain-language requirement for questions and feedback), brief gap 4 (state Demo Mode limits openly), and lecturer gaps 1 to 4 (key screen list with sketches deferred to bmad-ux, a short cost note, test PDF extraction with a real PowerPoint export before building the summary, and FR numbers carried into stories and tests).
For brief gaps 2 and 3 and lecturer gap 5, add a short reference to the brief instead of repeating it.
Add Medium 4 and any remaining medium findings to the open questions, noting that quality judgement by a single builder is a known limit of a solo project.
Save the lecturer-feedback check as reconcile-tilbakemelding.md.
Show me a summary of the changes when done. Do not commit.

Hvorfor slik: Jeg valgte selv hvilke funn som skulle rettes nå, hvilke som skulle henvise til briefen, og hvilke som skulle utsettes. Ikke alle KI-funn ble godtatt som de var.

Prompt 12: Avklaring og beslutning om store PDF-er

En melding ("Code") ble sendt ved et uhell, og KI-en spurte hva jeg mente i stedet for å gjette. Jeg svarte:

Sorry, "Code" was sent by mistake. I mean option 2: finish the PRD first.
I confirm all the values added during the review pass in §11.
For 31 to 50 page PDFs, the Summary must be ready in under 120 seconds. Add this to FR-8, remove the [NOTE FOR PM], and close open question 6.
Then continue with the open-item triage, the polish pass and setting status: final. Show me a summary when done. Do not commit.

Hvorfor: Gjennomgangen viste at kravene ikke sa noe om tid for PDF-er mellom 31 og 50 sider. Grensen på 120 sekunder er min beslutning.

Prompt 13: Beholde avsnitt 12

I poleringen fjernet KI-en avsnitt 12 (oversikten over omnummererte krav). Jeg ba om å beholde det:

Section 12 is still in prd-recall.md. Keep it, it is useful for reading the review files. Please check:
1. whether status is "final" in the header,
2. whether the other polish edits were applied,
3. that no sentence in the PRD says the FR mapping is only in .memlog.md; if one does, point it to section 12 instead.
Fix anything missing and show me the result. Do not commit.

Hvorfor: Gjennomgangsfilene bruker de gamle kravnumrene. Uten avsnitt 12 kan en leser ikke koble funnene til riktige krav.

Resultat: PRD med status "final", committet av meg ("Finalize PRD after review").

Oppsummering
Alle endringer ble kontrollert av meg før commit. Claude Code fikk aldri lov til å committe.
Jeg avviste KI-forslag fire ganger i økt 2 (korreksjon 1, korreksjon 2 to ganger, og avsnitt 12), og tok selv beslutningene om grenseverdier og hvilke gjennomgangsfunn som skulle rettes.
Komplette økter eksporteres med /export i Claude Code og lagres i denne mappen.