---
name: Recall
status: draft
sources:
  - ../brief-recall/brief-recall.md
  - ../prd-recall/prd-recall.md
  - ../../../tilbakemelding-product-brief.md
created: 2026-10-16
updated: 2026-10-16
---

# Recall — Experience Spine

> Paired with `DESIGN.md` (visual identity; tokens referenced as `{path.token}`). Wireframes in `wireframes/`. **The spines win over the wireframes on any conflict.** FR numbers refer to `prd-recall.md`.

## Foundation

Responsive web app (desktop and phone width). English interface. The summary and questions are in the language of the slides (English or Norwegian, PRD §4.3). No UI library is named; build with plain accessible HTML patterns. Light mode only in v1. Posture: coursework project, calm and supportive, never exam-like.

Design driver: the second-language student (PRD §2.1). The busy student gets the same flow.

## Information Architecture

| Surface | Reached from | Purpose | PRD |
|---|---|---|---|
| Log in / Register | App start when logged out | Account access; "Try the demo" button | FR-1, FR-23 |
| My lectures | Top bar, after login | List of saved lectures, status, delete | FR-20, FR-21 |
| Upload | Top bar "Upload" | Choose a PDF, see limits, accept AI notice | FR-3 to FR-7 |
| Processing | After upload | Real steps while the summary is made; failure and retry | FR-5, FR-8 |
| Lecture page (hub) | My lectures, after processing | Tabs: Summary, Multiple choice, Fill in the gaps, Essay, Results | FR-8 to FR-22 |
| — Summary tab | Lecture page | Parts, source chips, key terms panel, AI notice | FR-8, FR-9, FR-11 |
| — Quiz tabs (3) | Lecture page | One question at a time, instant check | FR-12 to FR-17 |
| — Results tab | Lecture page, end of a quiz | Score, essay attempts, review list | FR-18, FR-19 |
| Report a question | From any question | Short reason form | FR-22 |
| Demo | "Try the demo" | Same screens with the example lecture and a banner | FR-23 |

Top bar on every logged-in screen: logo "Recall", "My lectures", "Upload", "Text size" control (A, A+, A++), "Log out". On a phone: a "Menu" button with a text label opens the same items; the Text size control stays visible next to it.

The lecture page is the hub. The tab row is always visible. The student can switch tabs at any time and come back to where they were. Deep links open the Summary tab at the right part (anchor to the part heading).

→ Wireframes: `wireframes/01-login.md`, `02-my-lectures.md`, `03-upload.md`, `04-processing.md`, `05-summary.md`, `06-quiz-multiple-choice.md`, `07-quiz-fill-in-the-gaps.md`, `08-quiz-essay.md`, `09-results.md`.

## Voice and Tone

Rules for all interface text (microcopy). Brand posture is in `DESIGN.md`.

- Short, literal sentences. Aim for 12 words or fewer.
- One idea per sentence. Active voice. Present tense.
- Common words. No idioms, slang, jokes, metaphors or phrasal verbs ("sign up", "give it a go").
- Say what to do, then why. Name the object ("Choose a PDF"), not "it".
- No exclamation marks. No timers or countdown wording ("hurry", "only 2 minutes left").
- Calm words for wrong answers: "Not quite yet", never "Wrong", "Incorrect" or "Failed".
- Use the same word for the same thing everywhere (see table).

| Use | Not |
|---|---|
| Log in / Log out | Sign in, Sign off |
| Register | Sign up |
| Lecture | Class, Session |
| Summary | Recap, Overview |
| Key terms | Vocabulary, Glossary |
| Slides 12 to 15 | Pp. 12–15 |
| Check answer | Submit, Grade |
| Not quite yet | Wrong, Incorrect |
| Read this part again | Revisit, Review the material |
| Review list | Weak topics |

Example messages:

| Moment | Text |
|---|---|
| Correct | "Correct. Well done." |
| Not correct | "Not quite yet. The correct answer is shown below." |
| Scanned PDF | "This file has no text we can read. Choose a PDF with text, not a scan." |
| Too long | "This PDF has more than 50 pages. Choose a shorter file." |
| Too large | "This file is larger than 10 MB. Choose a smaller file." |
| Daily limit | "You have used your 5 uploads for today. You can upload again tomorrow." |
| Processing failed | "We could not make the summary. Please try again." |
| AI notice (summary/quiz) | "This text was made by AI. It can contain mistakes. Check it against your slides." |
| AI notice (upload, first time) | "Recall sends your slides and your essay answers to an AI service. Do not upload files you are not allowed to share." |
| Register note | "We can't reset passwords yet. Please remember yours." |
| Essay hint | "Write 2 to 5 sentences. Spelling and grammar are not marked." |
| No wrong answers | "You answered everything correctly. There is nothing to review." |

## Component Patterns

Behavioural rules. Visual specs are in `DESIGN.md.Components`.

| Component | Use | Behavioural rules |
|---|---|---|
| Top bar | All logged-in screens | Fixed order. Active item has text style, not colour only. |
| Text size control | Top bar | Three levels: normal 18px, large 22px, extra large 26px. Applies at once to the whole app, including quiz screens, and is remembered on this device. The button states its current level in text ("Text size: Large"). |
| Tabs | Lecture page | Selected tab has `aria-selected` and underline. Keyboard: arrow keys move, Enter or Space selects. Quiz progress is kept when switching tabs (see Interaction Primitives). Tab labels: Summary, Multiple choice, Fill in the gaps, Essay, Results. Phone short labels: Summary, Choice, Gaps, Essay, Results. |
| Jump to list | Top of Summary tab | Lists all part headings as links. Links move focus to the part heading. |
| Summary part | Summary tab | Heading, 2 to 5 short paragraphs, source chip, then the key terms panel for that part. |
| Key terms panel | Beside each part (wide screen), below the part (phone) | Lists only the terms from that part. Each term: bold word + one plain sentence. Always visible, not collapsed. |
| Source chip | Summary parts, questions, feedback, review list | Text such as "Slides 12 to 15". Is a link to the matching summary part. Opens in the Summary tab and does not leave the lecture. |
| Question card | Quiz tabs | One question at a time. Shows "Question 3 of 10" in text. "Check answer" button, then "Next question". |
| Answer option | Multiple choice | Radio group with a visible group label (the question). Choose one, then "Check answer". |
| Gap input | Fill in the gaps | One visible label ("Type the missing word"). Matching rules (FR-15) are applied after "Check answer". The hint "Capital letters and extra spaces do not matter." is shown under the field. |
| Essay box | Essay tab | See Essay behaviour below. |
| Feedback card | After checking | Result line (icon + words), correct answer, one-sentence reason, source chip, then "Next question". |
| Report link | On every question | Text link "Report this question" opens a short form (reason, up to 300 characters) and shows "Thank you. We will look at it." |
| Lecture row | My lectures | Title, date, status ("Ready" or "Processing…"), buttons "Open" and "Delete". |
| Delete confirmation | My lectures | Dialog: "Delete this lecture? This removes the summary and all your results. You cannot undo this." Buttons "Delete lecture" and "Keep lecture". Focus starts on "Keep lecture". |
| Notice banner | Upload, Summary, Quiz, Demo | Icon and text. AI notice is shown on Summary and Quiz tabs. Demo banner is shown on every page in Demo Mode and cannot be closed. |

### Essay behaviour

- One essay question at a time (2 per lecture). Large text box (at least 8 lines), hint always visible.
- "Get feedback" is enabled when the box is not empty. An empty or one-word answer is still allowed and gets the lowest rating with all key points listed (FR-17).
- While waiting: "Reading your answer…" with the label "In progress". No timer.
- Feedback appears below the answer in three blocks, in this order: **What you explained well**, **What is missing**, **Read this part again** (source chip link). Language errors are never mentioned (FR-17).
- The student can edit the answer and press "Get feedback again". **Maximum 3 attempts per question.** The button shows "Attempt 2 of 3". After attempt 3 the box becomes read-only and the text says "You used all 3 attempts for this question."
- Earlier attempts stay visible below, newest first, each with its answer text and its feedback, folded under a heading "Attempt 1" etc. that can be opened. Folding is by button, with the state stated in text.
- Demo Mode: the student selects one of the prepared example answers and presses "Get feedback". Free typing is off, with the note "In demo mode you can only choose prepared answers." The 3-attempt rule is the same.

## State Patterns

| State | Surface | Treatment |
|---|---|---|
| Empty list | My lectures | "You have no lectures yet." and a primary button "Upload a lecture". Also a link "Try the demo". |
| Processing | Processing; My lectures row | Steps: "Reading your PDF", "Finding the key points", "Writing the summary". Done steps show a check icon. The current step shows "In progress". No percentage. The page says "You can leave this page. We keep working." The row in My lectures shows "Processing…". On ready, the processing page moves to the Summary; in the list the row changes to "Ready". |
| Processing failed | Processing; row | Message, button "Try again", link "Choose another file". No partial summary (FR-5). Row shows "Failed" with the same buttons. |
| Upload rejected | Upload | Message under the file field, with icon, plain reason (examples in Voice and Tone). The file field stays. Nothing is created. |
| Not accepted notice | Upload | "Upload a lecture" is disabled until the checkbox "I understand that my slides are sent to an AI service" is checked. The disabled button is explained in text next to it. |
| Daily limit | Upload | Message in place of the form. |
| Quiz not made yet | Quiz tab, first open | "We are making your questions." with "In progress". Then the first question. Questions are stored for later (PRD §4.4). |
| Quiz failed | Quiz tab | "We could not make the questions. Please try again." + "Try again". |
| Answer correct | Feedback card | Icon check + "Correct. Well done." Source chip. |
| Answer not correct | Feedback card | Icon + "Not quite yet." Shows the correct answer and a source chip. Same card layout as correct; nothing flashes or shakes. |
| Unanswered | Multiple choice | "Check answer" is disabled until an option is chosen, with the text "Choose one answer first." Skipping with "Skip question" counts as not answered (FR-13). |
| Quiz finished | End of quiz | Message "You finished this quiz." and button "See your results". |
| Results, nothing wrong | Results tab | "You answered everything correctly. There is nothing to review." (FR-19) |
| No attempt yet | Results tab | "You have not taken a quiz yet. Choose a quiz tab to start." |
| Logged out | Any protected page | Move to Log in; no lecture data is shown (FR-2). |
| Not found | Other user's lecture | "We can't find this lecture." (no hint that it exists) |
| Demo Mode | Every page | Banner: "Demo mode. Only the example lecture is available. Essay feedback is prepared in advance. Uploading and typing your own essay answers need an API key." |
| Offline / server error | Any | "We could not reach the server. Check your internet and try again." + "Try again". Answers already typed stay in the page. |

## Interaction Primitives

- **Pace belongs to the student.** There are no timers, countdowns, time limits or auto-advance anywhere. The student moves on only by pressing "Next question" (or the next tab).
- **Instant check (multiple choice, fill in the gaps).** "Check answer" shows the feedback card at once. The answer cannot be changed after checking. Focus moves to the feedback card; screen readers announce the result line through a polite live region.
- **Progress is kept.** Quiz state (current question, answers given, essay text) is saved when the student switches tabs, reloads, or leaves and returns. An unfinished quiz is resumed at the same question. Retake: button "Start again" on the Results tab starts a new attempt with the same stored questions.
- **Navigation inside a quiz.** "Back" returns to a previous question and shows its result read-only. A progress text "Question 3 of 10" is shown; no bar.
- **Source links.** Every source chip and the "Read this part again" link opens the Summary tab, scrolls to the part and moves keyboard focus to its heading. A link "Back to your question" returns to the quiz at the same question (a plain link, no history tricks).
- **Keyboard.** Everything works with Tab, Shift+Tab, Enter, Space and arrow keys (radio groups, tabs). Visible focus ring always (`{colors.focus}`, 3px).
- **Motion.** The only animation is a 150ms fade when feedback appears. With `prefers-reduced-motion`, there is no animation and no smooth scrolling. No spinners that spin forever; waiting states use text plus a static icon.
- **Text size.** Changing it never moves the student away from the current question.
- **Reporting.** "Report this question" opens inline under the question, not a new page, and keeps the quiz state.

## Accessibility Floor

Behavioural floor. Visual contrast is specified in `DESIGN.md.Colors`. Target is WCAG 2.1 AA (PRD §6.3), checked with Lighthouse (score 90 or higher) on the main pages, with a manual keyboard pass.

- Every page has one `h1`, ordered headings, a "Skip to main content" link, and landmarks (header, nav, main).
- All form fields have a visible text label that is programmatically linked. Errors are linked with `aria-describedby` and use icon plus words. Focus moves to the first error after a failed submit.
- Language: the interface is `lang="en"`. The summary and questions carry the lecture language (`lang="en"` or `lang="nb"`) so screen readers pronounce them correctly.
- Status messages (processing steps, feedback result, report sent) use a polite live region.
- Icons are decorative (`aria-hidden`) because the label always sits next to them.
- Touch targets are at least 48px.
- Zoom to 200% and the text size control to "Extra large" cause no loss of content or function and no sideways scrolling (except the tab row on a phone).
- No content depends on colour, hover, or timing.
- Reading load: short sentences, one idea per card, no idioms (see Voice and Tone). Summary and feedback text come from the AI prompts that require plain language (FR-10).
- Passwords: paste is allowed, "Show password" checkbox is provided, autocomplete attributes are set.

## Responsive & Platform

| Width | Layout |
|---|---|
| Phone (under 600px) | One column. Top bar collapses to a "Menu" button plus the Text size control. Tab row scrolls horizontally, short labels, with an edge fade. Key terms panel sits below its summary part. Buttons are full width. |
| Tablet and desktop (600px and wider) | Centred column (max 720px) for quiz, login, upload and results. Summary uses up to 1040px: part text on the left, key terms panel on the right of each part. |

Browsers: current Chrome, Firefox, Edge and Safari (PRD §6.3).

## Reading Support for Second-Language Students

Product-specific section.

- Key terms panel beside every summary part (not hidden behind taps).
- Text size control with three levels.
- Icons always with a text label.
- Interface wording is short and literal; there is no interface glossary.
- Essay feedback is about content, never language errors.
- Every claim shows its source slides, so the student can check the AI against the material.
- Quiz question wording avoids double negatives and idioms (FR-10).

## Key Flows

### Flow 1 — Amara checks what she understood (UJ-1)

Protagonist: Amara, an international student at Høgskolen i Molde, studying in English, her second language.

1. Amara opens Recall in the evening. She chooses **Log in**, types her email and password, and presses "Log in".
2. She lands on **My lectures** and presses "Upload a lecture". On first upload she reads the AI notice, ticks the box, and chooses the databases PDF (30 slides).
3. The **Processing** page shows three steps. She reads "You can leave this page. We keep working." and stays. After about 40 seconds the Summary opens.
4. On the **Summary** tab she uses "Jump to" and reads five parts. Each part has a key terms panel next to it. She reads "functional dependency" in the panel instead of looking it up.
5. She opens **Multiple choice**. For question 3 she picks an answer and presses "Check answer". She sees "Not quite yet", the correct answer, and a chip "Slides 12 to 15". She presses "Next question". She finishes with 7 of 10.
6. She opens **Fill in the gaps** and types "normalisaton"; it is accepted as correct (one wrong letter, FR-15). She finishes the 8 questions.
7. On the **Essay** tab she reads "Explain why we normalise a database", writes four sentences, and presses "Get feedback".
8. **Climax:** under her answer she reads "What you explained well: you explained repeated data." and "What is missing: update anomalies." and "Read this part again: Slides 12 to 15". She follows the link, rereads the part, returns, edits her answer, and presses "Get feedback again" (attempt 2 of 3). Now the missing block is empty.
9. On the **Results** tab she sees her scores, "Attempt 1: 1 of 2 points, Attempt 2: 2 of 2 points", and a review list with "Third normal form — Slides 16 to 18". She opens it and is taken to that part.
10. **Resolution:** the lecture and results are saved in My lectures. She logs out.

Edge: at step 2 she chooses a scanned PDF by mistake and sees "This file has no text we can read. Choose a PDF with text, not a scan." She chooses the right file.

### Flow 2 — Examiner tries the demo

Protagonist: Thomas, the examiner, with no account and no API key.

1. He opens the app and sees **Log in** with a clear "Try the demo" button.
2. He presses it. The example lecture opens on the **Summary** tab. The demo banner is at the top of every page.
3. He takes a multiple choice and a fill in the gaps quiz and sees the instant checks.
4. **Climax:** on the Essay tab, he selects a prepared example answer and presses "Get feedback". The three feedback blocks appear. He tries "Upload", and sees "Processing needs an API key" with a link to the README.
5. **Resolution:** he opens Results, sees the score and review list, and knows what the app does without any setup.

### Flow 3 — Recovering from a failed summary

Protagonist: Amara, on a weak campus connection.

1. She uploads a 45-page PDF. The Processing page shows the steps.
2. The AI service returns unusable output twice (FR-27).
3. **Climax:** the page shows "We could not make the summary. Please try again." with the buttons "Try again" and "Choose another file". No partial summary appears.
4. She presses "Try again" and the steps start again; the summary opens.

## If Time (UX items, in order)

1. Tap or hover on a key term inside the summary text to show its simple explanation (the key terms panel remains the main support).
2. Dark mode.
3. (From PRD) spaced repetition, exam plan, flashcards from key terms.

## Open Items and PRD Follow-ups

These come from decisions in this UX run. They are not yet in the PRD; update `prd-recall.md` (not done here).

1. **Essay resubmit rule.** Up to 3 attempts per essay question; the last attempt counts for the score and review list; all attempts are shown on Results. PRD FR-17, FR-18, FR-19, the Attempt definition and the cost notes (§6.2) need this. Also check the FR-29 evaluation: the evaluation assesses each prepared answer three times; that is unrelated to the 3 student attempts, but the wording should be kept clearly separate.
2. **Demo access vs FR-2.** FR-2 says a logged-out request returns no lecture data; FR-23 says a visitor opens the example lecture. State that the example lecture is public, read-only and exempt from FR-2.
3. **"Try the demo" with an API key.** The button is always visible (decision). The PRD says Demo Mode is used when no key is configured; clarify that the button opens the demo in every setup.
4. **Background processing.** Processing continues if the student leaves the page, and the lecture shows "Processing…" in My lectures. This is a requirement for the architecture step (job runs outside the page request).
5. **Text size and quiz progress storage.** Text size is kept on the device. Quiz progress must survive tab switches and reloads, so it is stored with the account, not only in the page.
6. **Essay points.** Open question 7 in the PRD (ratings of only 0 to 2 points with 2 key points) affects the results display "x of y points". Resolve when the Test Set essays are frozen.
7. **Skip question.** Multiple choice has a "Skip question" button (counts as wrong, FR-13). Confirm this is wanted.
