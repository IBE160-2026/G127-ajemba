---
title: Recall
status: draft
created: 2026-10-06
updated: 2026-10-06
---

# PRD: Recall

## 0. Document Purpose

This PRD defines version 1 of Recall for the builder (a solo student on the IBE160 course), the lecturer and examiner who grade the project, and the downstream BMAD steps (UX, architecture, epics and stories). It builds on `brief-recall/brief-recall.md` and on the lecturer's feedback (`tilbakemelding-product-brief.md`); it does not repeat them. Vocabulary is anchored in the Glossary (§3). Features are grouped with numbered functional requirements (FR-N) nested inside, and each has testable consequences. Section 5 is the dedicated section on how the quality of the AI's output is checked, as the lecturer asked. Every inferred decision was confirmed by the builder on 2026-10-06 and is recorded in §11.

## 1. Vision

Recall is a web app that turns a lecture PDF into a plain-language summary of the key points and then tests the student's understanding with three kinds of questions: multiple choice, fill-in-the-gaps, and essay questions with written feedback. A student uploads the slides after a lecture and in about fifteen minutes knows what they understood and where to spend their study time.

It is built first for students who study in a second language. Lecture slides are dense and written as speaking notes, so these students lose time decoding the text before they can learn from it, and they often reread passively. Recall replaces that with self-testing (retrieval practice), which research shows works well but which students rarely do because writing good questions is slow.

There is no technical moat; the same AI models are available to everyone. The value is focus and design: one job ("I just had a lecture, help me learn it"), plain language, three levels of testing in one flow, and every summary part, question and piece of feedback pointing back to the slides it came from, so the student can check the AI instead of trusting it.

## 2. Target User

### 2.1 Jobs To Be Done

- When a lecture has just ended, I want a short, clear overview of what mattered, so I do not have to decode dense slides in my second language.
- When I think I understand a topic, I want to be tested on it, so I find out what I can actually explain before the exam does.
- When I get something wrong, I want to be sent back to exactly the part of the lecture to revisit, so I spend my limited study time where it counts.
- When I do not fully trust an AI answer, I want to see which slides it is based on, so I can check it myself.

The primary user is the university student studying in a second language. The secondary user, the busy student combining study with work or family, uses the same flow; there is no separate design for them. the lecturer asked to choose one primary user or explain the design implications for each; this PRD treats the second-language student as the only design driver and the busy student as served by the short flow.

### 2.2 Non-Users (v1)

- Students whose lectures are only available as scanned or handwritten PDFs, audio or video.
- Groups or classes who want to share quizzes.
- Lecturers who want to author or grade quizzes for a course.

### 2.3 Key User Journeys

- **UJ-1. Amara finds out in fifteen minutes what she understood from Tuesday's lecture.**
  - **Persona + context:** Amara is an international student at Høgskolen i Molde studying IT and digitalisation in English, her second language. On Tuesday she had a 40-slide databases lecture on normalisation.
  - **Entry state:** She already has an account. She is on the web app on her laptop that evening with the lecture PDF.
  - **Path:** She logs in and uploads the PDF. Within a minute she sees a plain-language summary in short parts, each showing the slides it comes from, with a list of key terms ("functional dependency", "third normal form") and a simple explanation of each. She reads it in about five minutes. She takes the multiple choice quiz and gets 7 of 10. She does the fill-in-the-gaps quiz, typing key terms herself. She answers one essay question, "Explain why we normalise a database", in her own words.
  - **Climax:** The essay feedback says she explained redundancy well but missed update anomalies, and links to the summary part covering slides 12 to 15. The results page shows her score and a review list of two topics: update anomalies and third normal form.
  - **Resolution:** She opens the first review topic, which takes her back to that summary part, rereads it, and opens slides 12 to 15 in her own copy. The lecture and her results are saved to her account for exam revision. The session takes about fifteen minutes.
  - **Edge case:** She uploads a scanned PDF by mistake; the app rejects it with a clear message saying the file has no readable text, and she uploads the right file.

## 3. Glossary

- **Lecture** — One uploaded PDF owned by one **User**, with its **Summary**, **Questions** and **Attempts**.
- **User** — A registered person with an account. Sees only their own **Lectures** and **Attempts**.
- **Slide** — One page of the lecture PDF. Page number and slide number are the same. one PDF page equals one slide.
- **Summary** — The plain-language overview of a **Lecture**, made of **Summary Parts** and **Key Terms**.
- **Summary Part** — A short section of the **Summary** about one topic, with its **Source Reference**.
- **Source Reference** — The slide numbers a **Summary Part** or **Question** is based on, for example "slides 12 to 15".
- **Key Term** — A term from the lecture, listed with a short, simple explanation.
- **Question** — One quiz item of type **Multiple Choice**, **Fill-in-the-Gaps** or **Essay**. Each links to the **Summary Part** it comes from.
- **Multiple Choice** — A **Question** with four options and exactly one correct option.
- **Fill-in-the-Gaps** — A **Question** with a sentence missing a **Key Term** the student types.
- **Essay** — A **Question** the student answers in free text and receives **Essay Feedback** for.
- **Essay Feedback** — The written assessment of an essay answer: what is correct, which key points are missing, and which **Summary Part** to revisit, plus an **Essay Rating**.
- **Essay Rating** — The number of the **Essay Question**'s **Reference Key Points** that the answer covers. A higher number means a better answer. the rating is a count of covered key points, which makes "good rated above weak" directly checkable.
- **Attempt** — One run through a quiz type for a **Lecture**, with the student's answers, score and **Review List**.
- **Review List** — The topics the student should revisit after an **Attempt**, each linked to a **Summary Part**.
- **Demo Mode** — A run mode with no API key that serves a pre-processed example **Lecture**.
- **Test Set** — The fixed test **Lectures**, their **Reference Key Points** and prepared essay answers (§5).
- **Reference Key Point** — A main point of a test **Lecture** (or an essay question's expected point), written down by the builder before any AI output is generated.
- **Prompt** — The instruction text sent to the AI for summaries, questions or essay feedback. Stored as a versioned file.

## 4. Features

### 4.1 Accounts and Privacy of Lectures

**Description:** A student registers and logs in. Lectures and results are saved to the account and are private. Realizes UJ-1. authentication is email and password using an established, well-documented library; no email verification and no password reset in v1. This resolves the lecturer's open question: saved lectures require login.

#### FR-1: Register, log in and log out

A visitor can register with an email address and password, log in, and log out.

**Consequences (testable):**
- Registering with an email already in use is rejected with a clear message.
- Passwords are never stored in plain text.
- After logout, a saved-lecture page cannot be opened until the user logs in again.

#### FR-2: Lectures are private

A User can only see and open their own Lectures and Attempts.

**Consequences (testable):**
- A logged-out request for any Lecture, Summary or Attempt is redirected to login and returns no lecture data.
- A logged-in User requesting another User's Lecture or Attempt by ID receives a not-found or forbidden response and no data.

### 4.2 Upload and Validation

**Description:** The student uploads one PDF. The app checks it before spending any AI cost. Realizes UJ-1.

#### FR-3: Upload a PDF within limits

A User can upload one PDF of at most 50 pages and 10 MB.

**Consequences (testable):**
- A PDF over 50 pages is rejected with a message stating the page limit.
- A file over 10 MB is rejected with a message stating the size limit.
- A file that is not a PDF is rejected with a clear message.
- A rejected file creates no Lecture and makes no AI call.

#### FR-4: Reject PDFs without readable text

The app rejects a PDF whose extracted text is too small to be a text-based lecture. "too small" means fewer than 100 characters of extracted text per page on average; the exact threshold is tuned during testing with real slides.

**Consequences (testable):**
- A scanned (image-only) PDF is rejected with a message that the file has no readable text.
- A rejected file makes no AI call.

#### FR-5: Processing status and failure

While a Lecture is processed, the User sees that work is in progress. If processing fails, the User sees a clear message and can retry. no partial or half-finished Summary is ever shown; a failure shows an error and a retry button.

**Consequences (testable):**
- When the AI service is unreachable or returns unusable output after the retries in FR-23, the User sees an error message and a retry option, not an empty or partial Summary.

**Out of Scope:** Uploading several PDFs at once; merging lectures.

### 4.3 Summary

**Description:** The app produces a short plain-language Summary of the lecture, split into parts that each show their Source Reference, plus a list of Key Terms with simple explanations. Written for second-language readers: short sentences, plain words, key terms explained. Realizes UJ-1. the Summary is written in the language of the slides (English or Norwegian); the app's interface is English.

#### FR-6: Summary with source references

The app generates a Summary of an uploaded Lecture, in Summary Parts, each with a Source Reference.

**Consequences (testable):**
- A text-based PDF of up to 30 pages produces a Summary in under 60 seconds. measured with the real AI service on a normal connection; Demo Mode is exempt.
- Every Summary Part shows a Source Reference.
- Every slide number in a Source Reference exists in the PDF (checked automatically, see FR-23).

#### FR-7: Key terms with simple explanations

The Summary lists Key Terms, each with a short, simple explanation.

**Consequences (testable):**
- Each listed Key Term appears in the lecture text (checked automatically).
- Each Key Term has an explanation.

#### FR-8: Plain-language style

The Summary Prompt instructs the AI to use short sentences and plain words and to avoid unexplained jargon.

**Consequences (testable):**
- The instruction is present in the versioned Prompt file for summaries (FR-22).
- Plain-language quality is judged by the builder on the Test Set (§5), not by an automated readability score. no readability formula is enforced.

### 4.4 Multiple Choice

**Description:** Quick checks of facts and concepts (recognition). Realizes UJ-1. 10 Multiple Choice questions per Lecture, generated once when the student first opens that quiz type and then stored, so retakes use the same questions.

#### FR-9: Generate multiple choice questions

The app generates Multiple Choice questions from the Lecture, each linked to its Summary Part.

**Consequences (testable):**
- Each question has exactly four options and exactly one correct option.
- Each question has a link to a Summary Part and a Source Reference.
- Questions are generated in under 60 seconds.

#### FR-10: Score multiple choice

The app calculates the score of a Multiple Choice Attempt.

**Consequences (testable):**
- For a known set of answers, the displayed score equals the number of correct answers (for example 7 of 10).
- A question left unanswered counts as wrong.

### 4.5 Fill-in-the-Gaps

**Description:** Practice recalling key terms and definitions by typing them. Realizes UJ-1. 8 questions per Lecture, generated once and stored.

#### FR-11: Generate fill-in-the-gaps questions

The app generates Fill-in-the-Gaps questions in which one Key Term is missing from a sentence from the lecture, each linked to its Summary Part.

**Consequences (testable):**
- Each question has exactly one expected answer.
- Each question has a link to a Summary Part and a Source Reference.

#### FR-12: Check typed answers

The app checks a typed answer against the expected answer by fixed, deterministic rules (no AI involved).

**Consequences (testable):**
- Upper and lower case are ignored, and leading, trailing and extra spaces are ignored.
- For an expected answer of 5 letters or more, an answer with one wrong letter is accepted. "one wrong letter" means an edit distance of one: one letter replaced, added or removed.
- For an expected answer shorter than 5 letters, only an exact match (after the rules above) is accepted.
- Any other answer is marked wrong.
- Example tests: "Normalisation" expected, "normalisaton" accepted; "key" expected, "kay" rejected; "third normal form" expected, " Third  Normal Form " accepted.

### 4.6 Essay Questions with Feedback

**Description:** The student writes a short answer to an explanation question and receives written feedback on content and understanding, not on language mistakes (essential for second-language writers). Realizes UJ-1. 2 essay questions per Lecture, each generated together with its Reference Key Points (the points a good answer should contain), stored with the question.

#### FR-13: Generate essay questions

The app generates Essay questions from the Lecture, each with Reference Key Points and a link to a Summary Part.

**Consequences (testable):**
- Each Essay question has at least two Reference Key Points, each with a Source Reference.
- Each Essay question links to a Summary Part.

#### FR-14: Essay feedback

The app assesses a written answer and returns Essay Feedback and an Essay Rating.

**Consequences (testable):**
- The feedback states what the answer got right, which Reference Key Points are missing, and which Summary Part to revisit (with a link).
- Language errors (spelling, grammar) do not lower the Essay Rating and are not criticised in the feedback.
- For the prepared answers of the Test Set, the acceptance rules in §5 (FR-26) hold.
- An empty or one-word answer receives the lowest rating and feedback listing all key points as missing, without an unusable error.

### 4.7 Results and Review List

**Description:** After each quiz the student sees how they did and where to look next. Realizes UJ-1.

#### FR-15: Quiz results

After an Attempt, the app shows the score, and for each question whether it was correct and the correct answer (for Essay, the Essay Feedback).

**Consequences (testable):**
- The score shown equals the number of correct answers (Multiple Choice, Fill-in-the-Gaps). For Essay, the Essay Rating is shown as key points covered out of key points expected.

#### FR-16: Review List

After an Attempt, the app shows a Review List of topics to revisit.

**Consequences (testable):**
- Every Multiple Choice or Fill-in-the-Gaps question answered wrongly leads to a Review List entry for the Summary Part it comes from. Several wrong answers on the same Summary Part give one entry.
- Every Essay answer with at least one missing Reference Key Point leads to an entry for its Summary Part.
- Each entry links to its Summary Part and shows its Source Reference.
- An Attempt with no wrong answers shows a message instead of an empty list.

### 4.8 Saved Lectures

**Description:** Lectures and results are saved so the student can return before the exam. Realizes UJ-1.

#### FR-17: List saved lectures and results

A User can see a list of their saved Lectures and open each one to see its Summary and past Attempts.

**Consequences (testable):**
- The list shows only the logged-in User's Lectures.
- Opening a Lecture shows the stored Summary without a new AI call.
- Past Attempts show date, quiz type and score.

#### FR-18: Delete a lecture

A User can delete one of their Lectures, which removes its Summary, Questions, Attempts and the stored PDF text. deletion is a privacy safeguard worth including because lecture content is sent to an external service.

**Consequences (testable):**
- After deletion, the Lecture is gone from the list and its URL no longer returns data.

### 4.9 Reporting Wrong Questions

**Description:** The student can flag a question that looks wrong or unclear. This is how errors the Test Set misses are found (§5).

#### FR-19: Report this question

A User can report any Question with a short reason.

**Consequences (testable):**
- A report is stored with the Question, the Lecture, the User, the reason and a timestamp.
- The User sees a confirmation.
- The builder can list all reports. no admin screen in v1; reports are read from the database or an exported file by the builder.

### 4.10 Demo Mode and Running Locally

**Description:** The grader must be able to run the app without the builder's keys or paid accounts. Realizes UJ-1 with prepared data.

#### FR-20: Demo Mode

When no AI API key is configured, the app runs in Demo Mode with a pre-processed example Lecture (Summary, Questions and Essay Feedback already stored).

**Consequences (testable):**
- With no API key, the app starts, and a visitor can open the example Lecture, read its Summary, and take all three quiz types.
- In Demo Mode, uploading a new PDF shows a message that processing needs an API key.
- In Demo Mode, Essay Feedback is shown for prepared example answers selectable by the student. free-text essay answers cannot be assessed without an AI key, so Demo Mode offers prepared example answers to submit, with stored feedback.

#### FR-21: Run locally from the README

The repository allows another person to run the app locally following the README.

**Consequences (testable):**
- The repository contains a `.env.example` listing every setting, and a `.env` with real keys is excluded from Git.
- The README explains Demo Mode and how to use one's own API key.
- The repository contains a small test PDF made from the builder's own or freely licensed slides.
- A fresh clone followed step by step with the README starts the app in Demo Mode.

## 5. How the Quality of the AI's Output Is Checked

The AI produces the Summaries, Questions and Essay Feedback, so its output is checked, not trusted. Quality is handled in four layers: rules that run every time, a fixed Test Set the builder runs on purpose, the student's own ability to check the source, and reports from users. The most demanding part is Essay Feedback, because the AI assesses the student's free text.

### 5.1 What "good output" means

Quality is defined per output kind, so checks have something to compare against:

- **Summary:** covers the lecture's main points (completeness), says nothing the slides do not support (faithfulness), and is in plain language.
- **Questions:** are based on the lecture (grounded), have a single clear correct answer, and are linked to the right Summary Part.
- **Essay Feedback:** is correct about what the answer covers and misses, ranks better answers above worse ones, and points to the right Summary Part.

### 5.2 Test Set

#### FR-22: Versioned prompts

The Prompts for Summary, Questions and Essay Feedback are stored as files in the repository.

**Consequences (testable):**
- Each of the three tasks has its own Prompt file under version control.
- A change to a Prompt is a commit that can be traced; the evaluation (FR-25) records which Prompt version it ran against.

#### FR-24: Fixed test lectures

The Test Set contains three to five Lectures made from the builder's own or freely licensed slides, chosen to include at least one with messy PowerPoint-export text. the lecturer warned that slides exported from PowerPoint can give cluttered text, so at least one test lecture is a real PowerPoint export.

**Consequences (testable):**
- Before any AI output is generated for a test Lecture, its Reference Key Points are written down and committed (at least five per Lecture), so they cannot be shaped to fit the output.
- No copyrighted course material is in the repository.

### 5.3 Automatic checks (run every time the AI is called)

#### FR-23: Structure, grounding and retry

The app validates every AI response before showing or storing it.

**Consequences (testable):**
- Output that does not match the expected structure (for example a Multiple Choice question without four options, or a missing Source Reference) is rejected.
- Every slide number in a Source Reference exists in the PDF; every Key Term appears in the lecture text; every Question links to an existing Summary Part.
- A rejected response is retried automatically, at most twice. two retries. If still unusable, FR-5 applies and the User sees an error, never a wrong or partial result.
- These checks are covered by automated tests that feed in deliberately broken responses.

#### FR-29: Honest about uncertainty

The app tells the student that the content is AI-generated and may contain mistakes, and makes checking easy.

**Consequences (testable):**
- Summary and quiz pages show a short notice that content is AI-generated and should be checked against the slides.
- Every Summary Part, Question and piece of Essay Feedback shows its Source Reference.

### 5.4 Evaluation on the Test Set

#### FR-25: Evaluation run

The builder can run an evaluation that sends the Test Set through the real AI and records a report.

**Consequences (testable):**
- One command runs all Test Set Lectures and writes a report to a file in the repository, with the date and the Prompt versions used.
- The report shows, per Lecture, the results of the checks below.
- The evaluation needs an API key and is run by the builder; the stored report is available in the repository for the grader.

The checks, and their acceptance targets: the percentages are the builder's own targets and may be adjusted after the first runs, with the change logged.

- **Summary completeness:** the builder compares the Summary with the Reference Key Points. At least 80 % of the Reference Key Points of each test Lecture are covered.
- **Summary faithfulness:** the builder reads each Summary and marks statements the slides do not support. No unsupported statement in any Summary in the Test Set, and every one found is recorded.
- **Question grounding:** every generated Question is checked against the Reference Key Points and slide text. At least 90 % of Questions are based on a Reference Key Point or clearly on the slide text, and 100 % have exactly one correct answer (Multiple Choice) or one expected term (Fill-in-the-Gaps).
- **Source references:** 100 % of Source References are valid slides (automatic, FR-23); at least 90 % point to slides that actually contain the content (builder spot check of a sample of at least 10 per Lecture).

#### FR-26: Essay feedback calibration

For each test Lecture, the Test Set holds prepared answers to each Essay question: at least two good, two weak, and two containing a typical misunderstanding, each marked in advance by the builder with the Reference Key Points it covers. six answers per essay question.

**Consequences (testable):**
- In every test Lecture, every known good answer gets a higher Essay Rating than every known weak answer.
- Every known weak answer gets feedback naming at least one missing key point that matches a Reference Key Point.
- Every misunderstanding answer gets a lower Essay Rating than every known good answer, and its feedback names the missing or wrong point. this extends the brief's good-versus-weak rule to misunderstandings.
- The same prepared answer, assessed three times, never changes between good-above-weak and the reverse. the AI is not fully repeatable, so each answer is run three times to see if the ranking holds.
- A failure is a recorded finding that leads to a Prompt change (FR-27), not a hidden result.

#### FR-27: Re-run after every Prompt change

The evaluation (FR-25) is re-run after every change to a Prompt, and the results of the run before and after are kept in the repository.

**Consequences (testable):**
- The change log of each Prompt change names the evaluation report it was checked with.
- A Prompt change is not kept if it breaks a check that passed before. a fix of one check that breaks another is rolled back or reworked.

### 5.5 Checks without the AI

Logic that does not need the AI is tested with ordinary automated tests, so a wrong score is never caused by a model: Multiple Choice scoring (FR-10), Fill-in-the-Gaps matching (FR-12), Review List building (FR-16), PDF limits (FR-3, FR-4), and access control (FR-2). In these tests the AI is replaced by stored sample responses, so tests run without an API key or cost.

### 5.6 After release: user reports

#### FR-28: Handle reports

Reports from FR-19 are reviewed and acted on.

**Consequences (testable):**
- Each reported Question is reviewed by the builder; a Question confirmed as wrong is added to the Test Set as a regression case if it reveals a pattern the Test Set missed. with one builder and a course project, review is manual and occasional.

### 5.7 Limits of these checks

The Test Set covers a handful of lectures chosen by the builder, so it shows that the AI works on these lectures, not that it works on every lecture. Essay assessment is checked against the builder's own judgement of the prepared answers, which is the best available but not an independent expert. These limits are stated in the README so the grader can see what the checks do and do not prove. the README includes a short "what we checked and what we did not" section.

## 6. Cross-Cutting Requirements

### 6.1 Privacy and Data

- Lecture content and the student's essay answers are sent to an external AI service. The app states this clearly before upload. a one-time notice on the upload page that must be acknowledged on first upload.
- Passwords are handled by an established authentication approach and never stored in plain text.
- API keys are kept in `.env`, which is excluded from Git; `.env.example` is committed.
- Copyrighted course material is never added to the repository; test data is the builder's own or freely licensed slides.

### 6.2 Cost Guard

- The page and size limits (FR-3) keep each AI call bounded.
- A per-User daily upload limit protects against accidental cost. 5 uploads per User per day, adjustable in settings.

### 6.3 Accessibility and Readability

- The interface is in English with short sentences and plain words, to match the audience.
- The app targets WCAG 2.1 AA for contrast, keyboard navigation and form labels. AA is the target; no formal audit in v1.
- The layout works on a phone-width screen (responsive), in current versions of major browsers.

### 6.4 Performance

- Summary within 60 seconds for text-based PDFs of up to 30 pages (FR-6).
- Pages other than AI processing respond in under 2 seconds on a normal connection.

### 6.5 Testing and Repository

- Deterministic logic has automated tests (§5.5); the AI-dependent behaviour has the Test Set evaluation (§5.4).
- Documentation, test data and secrets have separate, documented places in the repository.
- The build order is: Summary, Multiple Choice, Fill-in-the-Gaps, Essay Feedback, so a working app exists early and the most time is left for Essay Feedback.

## 7. Non-Goals (Explicit)

- Not a general chat with a PDF; there is no free prompt field.
- Not a replacement for reading the lecture or textbook; Recall helps students find out what they understood.
- Not a tool that grades students for courses; Essay Feedback is for the student's own learning and is not an official assessment.
- Not building a technical moat or custom AI model; it uses an existing AI service.
- Not a language-learning tool; feedback does not correct spelling or grammar.

## 8. MVP Scope

### 8.1 In Scope

- Registration and login, with private lectures and results (FR-1, FR-2).
- Upload of a single text-based PDF within limits (FR-3 to FR-5).
- Plain-language Summary with Source References and Key Terms (FR-6 to FR-8).
- Quizzes in three formats (FR-9 to FR-14).
- Score and Review List (FR-15, FR-16).
- Saved lectures and results, and deletion (FR-17, FR-18).
- Report a wrong question (FR-19).
- Demo Mode, run-from-README (FR-20, FR-21).
- AI output quality checks (§5).

### 8.2 Out of Scope for MVP

- Scanned or handwritten PDFs (need text recognition; less reliable).
- Audio and video lecture recordings.
- Sharing quizzes with classmates or study groups.
- Integration with learning platforms such as Canvas.
- Mobile apps (v1 is a responsive web app).
- Payments and subscriptions.
- Email verification and password reset.
- An admin screen for reports.

**If time (in priority order):** spaced repetition (suggest when to review wrong topics); an exam plan combining all lectures in a course; flashcards generated from Key Terms.

## 9. Success Metrics

The lecturer asked for criteria that can be tested during the course, so every metric below is a test case. Launch metrics (active users, return rate, cost per user) belong to the long-term vision in the brief and are not v1 criteria.

**Primary**
- **SM-1**: Summary speed — a text-based PDF of up to 30 pages gives a Summary in under 60 seconds. Validates FR-6.
- **SM-2**: Source references — every Summary Part shows valid slide numbers and every Question links to a Summary Part (100 %, automatic). Validates FR-6, FR-9, FR-11, FR-13, FR-23.
- **SM-3**: Multiple choice — every question has four options with exactly one correct, and the score for a known set of answers is exactly right. Validates FR-9, FR-10.
- **SM-4**: Fill-in-the-gaps — the matching rules produce the expected result in all example tests in FR-12. Validates FR-12.
- **SM-5**: Essay feedback — on the Test Set, every good answer is rated above every weak answer, and every weak answer's feedback names at least one missing key point. Validates FR-14, FR-26.
- **SM-6**: Review list — every wrongly answered question leads to a Review List entry linked to the right Summary Part. Validates FR-16.
- **SM-7**: Accounts and access — a logged-out visitor, and one User asking for another's data, get no lecture data. Validates FR-1, FR-2.
- **SM-8**: Input limits and demo — PDFs over 50 pages or 10 MB and scanned PDFs are rejected with a clear message, and a fresh clone runs in Demo Mode from the README without keys. Validates FR-3, FR-4, FR-20, FR-21.

**Secondary**
- **SM-9**: AI output quality — the targets in FR-25 (80 % key-point coverage, 90 % grounded questions, no unsupported statements in any Summary in the Test Set) are met on the Test Set. Validates FR-25.
- **SM-10**: Prompt discipline — every Prompt change has an evaluation report from before and after. Validates FR-27.

**Counter-metrics (do not optimize)**
- **SM-C1**: Number of questions generated — more questions are not better; wrong or duplicate questions harm the student. Counterbalances SM-3, SM-9.
- **SM-C2**: Quiz score — a high score is not the goal and must never be raised by easier questions; the aim is for the student to see what they do not yet know. Counterbalances SM-5, SM-6.
- **SM-C3**: Summary length — a shorter Summary must not be reached by dropping Reference Key Points. Counterbalances SM-1.

## 10. Open Questions

1. Technology stack, AI service and storage are not chosen; this is decided in the architecture step, keeping to one web app with simple storage.
2. Which three to five lectures make up the Test Set? None are chosen. At least one should be a real PowerPoint export.
3. What is the deadline for the project? Unknown; it affects whether items in "If time" are realistic.
4. Does the extracted-text threshold in FR-4 (100 characters per page) work for real slides? To be tuned early with real slides.
5. How many Questions of each type are right? FR-9, FR-11 and FR-13 assume 10, 8 and 2; adjust after the first runs.

## 11. Confirmed Assumptions

*Every assumption made in the first draft. **The builder confirmed all of them on 2026-10-06**, with one change: the faithfulness target in FR-25 and SM-9 now reads "no unsupported statement in any Summary in the Test Set" (it first read "in most Summaries"). The summary language (the language of the slides) was also confirmed. The inline `[ASSUMPTION]` tags in §§0 to 10 have been removed; this list is the record of what was assumed. Confirmations and the change are logged in `.memlog.md`.*

- **§2.1** — The second-language student is the only design driver; the busy student uses the same flow. *(Confirmed 2026-10-06.)*
- **§3 Glossary (Slide)** — One PDF page equals one slide. *(Confirmed 2026-10-06.)*
- **§3 Glossary (Essay Rating)** — The rating is a count of covered Reference Key Points. *(Confirmed 2026-10-06.)*
- **§4.1** — Email-and-password authentication with an established library; no email verification, no password reset. *(Confirmed 2026-10-06.)*
- **FR-4** — Scanned PDF threshold: fewer than 100 characters of text per page on average. *(Confirmed 2026-10-06.)*
- **FR-5** — On failure, an error and a retry button; no partial Summary. *(Confirmed 2026-10-06.)*
- **§4.3** — The Summary is in the language of the slides; the interface is English. *(Confirmed 2026-10-06.)*
- **FR-6** — The 60-second target is measured with the real AI service; Demo Mode is exempt. *(Confirmed 2026-10-06.)*
- **FR-8** — No automated readability score; plain language is judged by the builder. *(Confirmed 2026-10-06.)*
- **§4.4 / FR-9** — 10 Multiple Choice questions, generated once and stored; generation under 60 seconds. *(Confirmed 2026-10-06.)*
- **§4.5** — 8 Fill-in-the-Gaps questions, generated once and stored. *(Confirmed 2026-10-06.)*
- **FR-12** — "One wrong letter" means an edit distance of one. *(Confirmed 2026-10-06.)*
- **§4.6** — 2 Essay questions per Lecture, each with stored Reference Key Points. *(Confirmed 2026-10-06.)*
- **FR-14** — An empty or one-word answer gets the lowest rating and all key points listed as missing. *(Confirmed 2026-10-06.)*
- **FR-18** — A delete-lecture function is included as a privacy safeguard. *(Confirmed 2026-10-06.)*
- **FR-19** — No admin screen; the builder reads reports from the database or an export. *(Confirmed 2026-10-06.)*
- **FR-20** — Demo Mode offers prepared example answers with stored feedback; free-text essays need an API key. *(Confirmed 2026-10-06.)*
- **FR-24** — At least one test Lecture is a real PowerPoint export. *(Confirmed 2026-10-06.)*
- **FR-23** — Two automatic retries on unusable AI output. *(Confirmed 2026-10-06.)*
- **FR-25 / SM-9** — The percentage targets (80 %, 90 %) are the builder's own and may be adjusted with a logged reason. *(Confirmed 2026-10-06.)*
- **FR-25 / SM-9 (changed on confirmation)** — The faithfulness target first read "no unsupported statements in most Summaries", which is not measurable. At the builder's request it now reads "no unsupported statement in any Summary in the Test Set". *(Changed and confirmed 2026-10-06.)*
- **FR-26** — Six prepared answers per essay question (two good, two weak, two misunderstanding); misunderstandings must rank below good answers; each answer is run three times. *(Confirmed 2026-10-06.)*
- **FR-27** — A Prompt change that breaks a previously passing check is rolled back or reworked. *(Confirmed 2026-10-06.)*
- **FR-28** — Report review is manual and occasional. *(Confirmed 2026-10-06.)*
- **§5.7** — The README includes a "what we checked and what we did not" section. *(Confirmed 2026-10-06.)*
- **§6.1** — A one-time notice on the upload page about external AI processing, acknowledged on first upload. *(Confirmed 2026-10-06.)*
- **§6.2** — 5 uploads per User per day. *(Confirmed 2026-10-06.)*
- **§6.3** — WCAG 2.1 AA as a target, with no formal audit. *(Confirmed 2026-10-06.)*
- **§6.4** — Pages other than AI processing respond in under 2 seconds. *(Confirmed 2026-10-06.)*
- **§8.2** — No email verification, password reset or admin screen in v1. *(Confirmed 2026-10-06.)*
