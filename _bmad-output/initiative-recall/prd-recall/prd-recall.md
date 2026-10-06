---
title: Recall
status: final
created: 2026-10-06
updated: 2026-10-06
---

# PRD: Recall

## 0. Document Purpose

This PRD defines version 1 of Recall for the builder (a solo student on the IBE160 course), the lecturer and examiner who grade the project, and the downstream BMAD steps (UX, architecture, epics and stories). It builds on `brief-recall/brief-recall.md` and on the lecturer's feedback (`tilbakemelding-product-brief.md`); it does not repeat them. The brief was revised after that feedback, and the repository history shows how the plan developed. Vocabulary is anchored in the Glossary (§3). Features are grouped with numbered functional requirements (FR-N) nested inside, and each has testable consequences. Section 5 is the dedicated section on how the quality of the AI's output is checked, as the lecturer asked. The builder confirmed every inferred decision on 2026-10-06; they are recorded in §11.

## 1. Vision

Recall is a web app that turns a lecture PDF into a plain-language summary of the key points and then tests the student's understanding with three kinds of questions: multiple choice, fill-in-the-gaps, and essay questions with written feedback. A student uploads the slides after a lecture and in about fifteen minutes knows what they understood and where to spend their study time.

It is built first for students who study in a second language. Lecture slides are dense and written as speaking notes, so these students lose time decoding the text before they can learn from it, and they often reread passively. Recall replaces that with self-testing (retrieval practice), which research shows works well but which students rarely do because writing good questions is slow.

There is no technical moat; the same AI models are available to everyone. The value is focus and design: one job ("I just had a lecture, help me learn it"), plain language, three levels of testing in one flow, and every summary part, question and piece of feedback pointing back to the slides it came from, so the student can check the AI instead of trusting it.

The longer-term vision (a study companion across a whole course, spaced review, professional learning), how students cope today, why the timing is right, the builder's closeness to the target group, and the post-launch success signs (active users, return rate, cost per user) are described in `brief-recall.md` (sections "The Problem", "What Makes This Different", "Vision") and are not repeated here.

## 2. Target User

### 2.1 Jobs To Be Done

- When a lecture has just ended, I want a short, clear overview of what mattered, so I do not have to decode dense slides in my second language.
- When I think I understand a topic, I want to be tested on it, so I find out what I can actually explain before the exam does.
- When I get something wrong, I want to be sent back to exactly the part of the lecture to revisit, so I spend my limited study time where it counts.
- When I do not fully trust an AI answer, I want to see which slides it is based on, so I can check it myself.

The primary user is the university student studying in a second language. The secondary user, the busy student combining study with work or family, uses the same flow; there is no separate design for them. The lecturer asked to choose one primary user or explain the design implications for each. This PRD treats the second-language student as the only design driver, and the busy student is served by the short flow.

### 2.2 Non-Users (v1)

- Students whose lectures are only available as scanned or handwritten PDFs, audio or video.
- Groups or classes who want to share quizzes.
- Lecturers who want to author or grade quizzes for a course.

### 2.3 Key User Journeys

- **UJ-1. Amara finds out in fifteen minutes what she understood from Tuesday's lecture.**
  - **Persona + context:** Amara is an international student at Høgskolen i Molde studying IT and digitalisation in English, her second language. On Tuesday she had a 30-slide databases lecture on normalisation.
  - **Entry state:** She already has an account. She is on the web app on her laptop that evening with the lecture PDF.
  - **Path:** She logs in and uploads the PDF. Within a minute she sees a plain-language summary in short parts, each showing the slides it comes from, with a list of key terms ("functional dependency", "third normal form") and a simple explanation of each. She reads it in about five minutes. She takes the multiple choice quiz and gets 7 of 10. She does the fill-in-the-gaps quiz, typing key terms herself. She answers one essay question, "Explain why we normalise a database", in her own words.
  - **Climax:** The essay feedback says she explained redundancy well but missed update anomalies, and links to the summary part covering slides 12 to 15. The results page shows her score and a review list of two topics: update anomalies and third normal form.
  - **Resolution:** She opens the first review topic, which takes her back to that summary part, rereads it, and opens slides 12 to 15 in her own copy. The lecture and her results are saved to her account for exam revision. The session takes about fifteen minutes.
  - **Edge case:** She uploads a scanned PDF by mistake; the app rejects it with a clear message saying the file has no readable text, and she uploads the right file.

Features that are not part of this journey (reporting a question, deleting a lecture, Demo Mode and running from the README) are operational. They exist for privacy, for the quality checks in §5 and for the grader, and are marked as such in §4.

## 3. Glossary

- **Lecture** — One uploaded PDF owned by one **User**, with its **Summary**, **Questions** and **Attempts**.
- **User** — A registered person with an account. Sees only their own **Lectures** and **Attempts**.
- **Slide** — One page of the lecture PDF. Page number and slide number are the same.
- **Summary** — The plain-language overview of a **Lecture**, made of **Summary Parts** and **Key Terms**.
- **Summary Part** — A short section of the **Summary** about one topic, with its **Source Reference**.
- **Source Reference** — The slide numbers a **Summary Part** or **Question** is based on, for example "slides 12 to 15".
- **Key Term** — A term from the lecture, listed with a short, simple explanation.
- **Question** — One quiz item of type **Multiple Choice**, **Fill-in-the-Gaps** or **Essay**. Each links to the **Summary Part** it comes from.
- **Quiz** — The set of **Questions** of one type for one **Lecture**. A student takes a **Quiz** as an **Attempt**.
- **Multiple Choice** — A **Question** with four options and exactly one correct option.
- **Fill-in-the-Gaps** — A **Question** with a sentence missing a **Key Term** the student types.
- **Essay** — A **Question** the student answers in free text and receives **Essay Feedback** for. It has **Reference Key Points**.
- **Essay Feedback** — The written assessment of an **Essay** answer: what is correct, which key points are missing, and which **Summary Part** to revisit, plus an **Essay Rating**.
- **Essay Rating** — The number of the **Essay**'s **Reference Key Points** that the answer covers. A higher number means a better answer, which makes "good rated above weak" directly checkable.
- **Attempt** — One run through a **Quiz** for a **Lecture**, with the student's answers, score and **Review List**.
- **Review List** — The topics the student should revisit after an **Attempt**, each linked to a **Summary Part**.
- **Demo Mode** — A run mode with no API key that serves a pre-processed example **Lecture**, with the limits stated in FR-23.
- **Test Set** — The fixed test **Lectures**, their **Reference Key Points**, their frozen **Essay** questions and the prepared essay answers (§5).
- **Reference Key Point** — A point a good answer or Summary should contain. For **Test Set** Lectures, the builder writes them down before any AI output is evaluated. For uploaded Lectures, the AI generates them together with each **Essay**.
- **Prompt** — The instruction text sent to the AI for summaries, questions or essay feedback. Stored as a versioned file.

## 4. Features

### 4.1 Accounts and Privacy of Lectures

**Description:** A student registers and logs in. Lectures and results are saved to the account and are private. Realizes UJ-1. Authentication is email and password using an established, well-documented library; there is no email verification and no password reset in v1. This resolves the lecturer's open question: saved lectures require login.

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

The app rejects a PDF whose extracted text is too small to be a text-based lecture. "Too small" means fewer than 100 characters of extracted text per page on average. This threshold is a starting value that is tuned with real slides.

**Consequences (testable):**
- A scanned (image-only) PDF is rejected with a message that the file has no readable text.
- A rejected file makes no AI call.
- Before the Summary feature is built, text extraction is run on at least one real PowerPoint-exported PDF, and the result (including how cluttered the text is) is recorded in the repository. The lecturer warned that such slides can give messy text.

#### FR-5: Processing status and failure

While a Lecture is processed, the User sees that work is in progress. If processing fails, the User sees a clear message and can retry. No partial or half-finished Summary is ever shown.

**Consequences (testable):**
- When the AI service is unreachable or returns unusable output after the retries in FR-27, the User sees an error message and a retry button, not an empty or partial Summary.

**Out of Scope:** Uploading several PDFs at once; merging lectures.

#### FR-6: Notice about external AI processing

Before a User's first upload, the app states that lecture content and essay answers are sent to an external AI service, and the User must acknowledge this.

**Consequences (testable):**
- A User who has not acknowledged the notice cannot upload a PDF.
- The notice is shown once, on the upload page, and again in the README.

#### FR-7: Daily upload limit

The app limits each User to 5 uploads per day to protect against accidental AI cost. The limit is a setting that can be changed.

**Consequences (testable):**
- A sixth upload by the same User on the same day is rejected with a clear message and makes no AI call.
- Rejected uploads (FR-3, FR-4) do not count towards the limit.

### 4.3 Summary and Transparency

**Description:** The app produces a short plain-language Summary of the lecture, split into parts that each show their Source Reference, plus a list of Key Terms with simple explanations. Written for second-language readers: short sentences, plain words, key terms explained. Realizes UJ-1. The Summary is written in the language of the slides (English or Norwegian); the app's interface is English.

#### FR-8: Summary with source references

The app generates a Summary of an uploaded Lecture, in Summary Parts, each with a Source Reference.

**Consequences (testable):**
- A text-based PDF of up to 30 pages produces a Summary in under 60 seconds, measured with the real AI service on a normal home or campus broadband connection. Demo Mode is exempt.
- Every Summary Part shows a Source Reference.
- Every slide number in a Source Reference exists in the PDF (checked automatically, see FR-27).
- A text-based PDF of 31 to 50 pages produces a Summary in under 120 seconds, measured the same way. The User sees a progress indicator while it is processed.

#### FR-9: Key terms with simple explanations

The Summary lists Key Terms, each with a short, simple explanation.

**Consequences (testable):**
- Each listed Key Term appears in the lecture text (checked automatically).
- Each Key Term has an explanation.

#### FR-10: Plain-language style

The Prompts for the Summary, the Questions and the Essay Feedback instruct the AI to use short sentences and plain words and to avoid unexplained jargon, so that second-language readers can follow without extra effort.

**Consequences (testable):**
- The instruction is present in each of the versioned Prompt files (FR-25).
- Plain-language quality of Summary, Questions and Essay Feedback is judged by the builder on the Test Set (§5), not by an automated readability score.
- Question wording avoids double negatives and idioms. The builder checks this on the Test Set.

#### FR-11: AI-generated content notice

Summary and Quiz pages tell the student that the content is AI-generated and may contain mistakes, and make checking easy.

**Consequences (testable):**
- Summary and Quiz pages show a short notice that the content is AI-generated and should be checked against the slides.
- Every Summary Part, Question and piece of Essay Feedback shows its Source Reference.

### 4.4 Multiple Choice

**Description:** Quick checks of facts and concepts (recognition). Realizes UJ-1. Each Lecture has 10 Multiple Choice questions, generated once when the student first opens that Quiz and then stored, so retakes use the same questions.

#### FR-12: Generate multiple choice questions

The app generates Multiple Choice questions from the Lecture, each linked to its Summary Part.

**Consequences (testable):**
- Each question has exactly four options and exactly one correct option.
- Each question has a link to a Summary Part and a Source Reference.
- Questions are generated in under 60 seconds.

#### FR-13: Score multiple choice

The app calculates the score of a Multiple Choice Attempt.

**Consequences (testable):**
- For a known set of answers, the displayed score equals the number of correct answers (for example 7 of 10).
- A question left unanswered counts as wrong.

### 4.5 Fill-in-the-Gaps

**Description:** Practice recalling key terms and definitions by typing them. Realizes UJ-1. Each Lecture has 8 questions, generated once and stored.

#### FR-14: Generate fill-in-the-gaps questions

The app generates Fill-in-the-Gaps questions in which one Key Term is missing from a sentence from the lecture, each linked to its Summary Part.

**Consequences (testable):**
- Each question has exactly one expected answer.
- Each question has a link to a Summary Part and a Source Reference.
- Questions are generated in under 60 seconds.

#### FR-15: Check typed answers

The app checks a typed answer against the expected answer by fixed, deterministic rules (no AI involved).

**Consequences (testable):**
- Upper and lower case are ignored, and leading, trailing and extra spaces are ignored.
- For an expected answer of 5 letters or more, an answer with one wrong letter is accepted. "One wrong letter" means an edit distance of one: one letter replaced, added or removed.
- For an expected answer shorter than 5 letters, only an exact match (after the rules above) is accepted.
- Any other answer is marked wrong.
- Example tests: "Normalisation" expected, "normalisaton" accepted; "key" expected, "kay" rejected; "third normal form" expected, " Third  Normal Form " accepted.

### 4.6 Essay Questions with Feedback

**Description:** The student writes a short answer to an explanation question and receives written feedback on content and understanding, not on language mistakes (essential for second-language writers). Writing the answer also lets the student practise explaining concepts in the course language. Realizes UJ-1. Each Lecture has 2 Essay questions, each generated together with its Reference Key Points (the points a good answer should contain) and stored with the question.

#### FR-16: Generate essay questions

The app generates Essay questions from the Lecture, each with Reference Key Points and a link to a Summary Part.

**Consequences (testable):**
- Each Essay question has at least two Reference Key Points, each with a Source Reference.
- Each Essay question links to a Summary Part.
- Essay questions are generated in under 60 seconds.

#### FR-17: Essay feedback

The app assesses a written answer and returns Essay Feedback and an Essay Rating.

**Consequences (testable):**
- The feedback states what the answer got right, which Reference Key Points are missing, and which Summary Part to revisit (with a link).
- Language errors (spelling, grammar) do not lower the Essay Rating and are not criticised in the feedback.
- For the prepared answers of the Test Set, the acceptance rules in FR-29 hold.
- An empty or one-word answer receives the lowest rating and feedback listing all key points as missing, and the User sees this feedback rather than an error page.

### 4.7 Results and Review List

**Description:** After each Quiz the student sees how they did and where to look next. Realizes UJ-1.

#### FR-18: Quiz results

After an Attempt, the app shows the score, and for each question whether it was correct and the correct answer (for Essay, the Essay Feedback).

**Consequences (testable):**
- The score shown equals the number of correct answers (Multiple Choice, Fill-in-the-Gaps). For Essay, the Essay Rating is shown as key points covered out of key points expected.

#### FR-19: Review List

After an Attempt, the app shows a Review List of topics to revisit.

**Consequences (testable):**
- Every Multiple Choice or Fill-in-the-Gaps question answered wrongly leads to a Review List entry for the Summary Part it comes from. Several wrong answers on the same Summary Part give one entry.
- Every Essay answer with at least one missing Reference Key Point leads to an entry for its Summary Part.
- Each entry links to its Summary Part and shows its Source Reference.
- An Attempt with no wrong answers shows a message instead of an empty list.

### 4.8 Saved Lectures

**Description:** Lectures and results are saved so the student can return before the exam. Realizes UJ-1 (the saving, as the final step); deletion is operational.

#### FR-20: List saved lectures and results

A User can see a list of their saved Lectures and open each one to see its Summary and past Attempts.

**Consequences (testable):**
- The list shows only the logged-in User's Lectures.
- Opening a Lecture shows the stored Summary without a new AI call.
- Past Attempts show date, Quiz and score.

#### FR-21: Delete a lecture

A User can delete one of their Lectures, which removes its Summary, Questions, Attempts and the stored PDF text. Deletion is a privacy safeguard, included because lecture content is sent to an external service. This feature is operational and is not part of UJ-1.

**Consequences (testable):**
- After deletion, the Lecture is gone from the list and its URL no longer returns data.

### 4.9 Reporting Wrong Questions

**Description:** The student can flag a question that looks wrong or unclear. This is how errors the Test Set misses are found (§5). This feature is operational and is not part of UJ-1.

#### FR-22: Report this question

A User can report any Question with a short reason.

**Consequences (testable):**
- A report is stored with the Question, the Lecture, the User, the reason and a timestamp.
- The User sees a confirmation.
- The builder can list all reports. There is no admin screen in v1; reports are read from the database or an exported file.

### 4.10 Demo Mode and Running Locally

**Description:** The grader must be able to run the app without the builder's keys or paid accounts. These features are operational and are not part of UJ-1; they use prepared data.

#### FR-23: Demo Mode

When no AI API key is configured, the app runs in Demo Mode with a pre-processed example Lecture (Summary, Questions and Essay Feedback already stored). The limits of Demo Mode are stated openly in the app and in the README.

**Consequences (testable):**
- With no API key, the app starts, and a visitor can open the example Lecture, read its Summary, and take all three Quizzes.
- A visible banner on every page in Demo Mode says that only the example Lecture is available, that essay feedback is prepared in advance, and that uploading and free-text essay assessment need an API key.
- In Demo Mode, uploading a new PDF shows a message that processing needs an API key.
- In Demo Mode, Essay Feedback is shown for prepared example answers that the student can select and submit. Free-text essay answers cannot be assessed without an AI key.

#### FR-24: Run locally from the README

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
- **Questions:** are based on the lecture (grounded), have a single clear correct answer that is actually correct, and are linked to the right Summary Part.
- **Essay Feedback:** is correct about what the answer covers and misses, ranks better answers above worse ones, and points to the right Summary Part.

### 5.2 Test Set

#### FR-25: Versioned prompts

The Prompts for Summary, Questions and Essay Feedback are stored as files in the repository.

**Consequences (testable):**
- Each of the three tasks has its own Prompt file under version control.
- A change to a Prompt is a commit that can be traced; the evaluation (FR-28) records which Prompt version it ran against.

#### FR-26: Test Set Lectures and frozen Essay questions

The Test Set contains three to five Lectures made from the builder's own or freely licensed slides, chosen to include at least one real PowerPoint export with messy text. For each Test Set Lecture, the builder writes the Reference Key Points and the Essay questions with their Reference Key Points, and freezes them in the repository.

**Consequences (testable):**
- Before any AI output is evaluated for a Test Set Lecture, its Reference Key Points (at least five per Lecture) and its Essay questions with their Reference Key Points are written down and committed, so they cannot be shaped to fit the output.
- The prepared essay answers (FR-29) are answers to these frozen Essay questions. The evaluation (FR-28) sends the frozen Essay questions and prepared answers to the Essay Feedback step only. The AI-generated Essay questions of FR-16, which real uploads use, are also generated for each Test Set Lecture and checked for grounding, but are not used for the answer ranking.
- No copyrighted course material is in the repository.

### 5.3 Automatic checks (run every time the AI is called)

#### FR-27: Structure, grounding and retry

The app validates every AI response before showing or storing it.

**Consequences (testable):**
- Output that does not match the expected structure (for example a Multiple Choice question without four options, or a missing Source Reference) is rejected.
- Every slide number in a Source Reference exists in the PDF; every Key Term appears in the lecture text; every Question links to an existing Summary Part.
- A rejected response is retried automatically, at most twice. If it is still unusable, FR-5 applies and the User sees an error, never a wrong or partial result.
- These checks are covered by automated tests that feed in deliberately broken responses.

### 5.4 Evaluation on the Test Set

#### FR-28: Evaluation run

The builder can run an evaluation that sends the Test Set through the real AI and records a report.

**Consequences (testable):**
- One command runs all Test Set Lectures and writes a report to a file in the repository, with the date and the Prompt versions used.
- The report shows, per Lecture, the results of the checks below.
- The evaluation needs an API key and is run by the builder; the stored report is available in the repository for the grader.

The checks and their acceptance targets follow. The percentages are the builder's own targets and may be adjusted after the first runs, with the change logged.

- **Summary completeness:** the builder compares the Summary with the Reference Key Points. At least 80 % of the Reference Key Points of each Test Set Lecture are covered.
- **Summary faithfulness:** the builder reads each Summary and marks statements the slides do not support. No unsupported statement in any Summary in the Test Set, and every one found is recorded.
- **Question grounding:** every generated Question is checked against the Reference Key Points and slide text. At least 90 % of Questions are based on a Reference Key Point or clearly on the slide text, and 100 % have exactly one correct answer (Multiple Choice) or one expected term (Fill-in-the-Gaps).
- **Answer-key correctness:** the builder checks the marked correct answer of every Multiple Choice question, and the expected term of every Fill-in-the-Gaps question, generated for the Test Set Lectures against the slides. 100 % are correct. Any wrong key is recorded as a finding.
- **Source references:** 100 % of Source References are valid slides (automatic, FR-27); at least 90 % point to slides that actually contain the content (builder spot check of a sample of at least 10 per Lecture).

#### FR-29: Essay feedback calibration

For each frozen Essay question of each Test Set Lecture, the Test Set holds prepared answers: at least two good, two weak, and two containing a typical misunderstanding, each marked in advance by the builder with the Reference Key Points it covers. This makes six prepared answers per Essay question.

**Consequences (testable):**
- In every Test Set Lecture, every known good answer gets a higher Essay Rating than every known weak answer.
- Every known weak answer gets feedback naming at least one missing key point that matches a Reference Key Point.
- Every misunderstanding answer gets a lower Essay Rating than every known good answer, and its feedback names the missing or wrong point. This extends the brief's good-versus-weak rule to misunderstandings.
- Each prepared answer is assessed three times, because the AI is not fully repeatable. The ranking must hold in all three runs.
- A failure is a recorded finding that leads to a Prompt change (FR-30), not a hidden result.

#### FR-30: Re-run after every Prompt change

The evaluation (FR-28) is re-run after every change to a Prompt, and the results of the run before and after are kept in the repository.

**Consequences (testable):**
- The change log of each Prompt change names the evaluation report it was checked with.
- A Prompt change is not kept if it breaks a check that passed before. A fix of one check that breaks another is rolled back or reworked.

### 5.5 Checks without the AI

Logic that does not need the AI is tested with ordinary automated tests, so a wrong score is never caused by a model: Multiple Choice scoring (FR-13), Fill-in-the-Gaps matching (FR-15), Review List building (FR-19), PDF limits (FR-3, FR-4), the upload limit (FR-7) and access control (FR-2). In these tests the AI is replaced by stored sample responses, so tests run without an API key or cost.

### 5.6 After release: user reports

#### FR-31: Handle reports

Reports from FR-22 are reviewed and acted on.

**Consequences (testable):**
- Each reported Question is reviewed by the builder. A Question confirmed as wrong is added to the Test Set as a regression case if it reveals a pattern the Test Set missed. With one builder on a course project, review is manual and occasional.

### 5.7 Limits of these checks

The Test Set covers a handful of lectures chosen by the builder, so it shows that the AI works on these lectures, not that it works on every lecture. The quality judgements in §5.4 (completeness, faithfulness, answer keys, and the marking of prepared essay answers) are made by a single builder. This is a known limit of a solo project: the judgement is the best available, but it is not that of an independent expert. The fifteen-minute claim and the second-language fit of the Summary are not measured in v1. These limits are stated in the README, in a short "what we checked and what we did not" section, so the grader can see what the checks do and do not prove.

## 6. Cross-Cutting Requirements

### 6.1 Privacy and Data

- Lecture content and the student's essay answers are sent to an external AI service. The app states this clearly before upload (FR-6).
- Passwords are handled by an established authentication approach and never stored in plain text (FR-1).
- API keys are kept in `.env`, which is excluded from Git; `.env.example` is committed.
- Copyrighted course material is never added to the repository; test data is the builder's own or freely licensed slides.

### 6.2 Cost

- The page and size limits (FR-3) and the daily upload limit (FR-7) bound the AI cost per User.
- Each processed Lecture makes several AI calls (Summary, three Quiz types, and one assessment per submitted essay answer). The evaluation run (FR-28, FR-29) costs more: every prepared essay answer is assessed three times, and the evaluation is re-run after each Prompt change (FR-30).
- To keep cost low: automated tests use stored sample responses (§5.5), the evaluation is run on demand and not automatically, Demo Mode needs no key, and the builder chooses a small, inexpensive model if the quality checks pass with it. A cost estimate is made once the AI service is chosen (§10).

### 6.3 Accessibility and Readability

- The interface is in English with short sentences and plain words, to match the audience.
- The layout is clean and readable: clear headings, short Summary Parts, generous spacing, no dense walls of text.
- The app targets WCAG 2.1 AA for contrast, keyboard navigation and form labels. There is no formal audit in v1; an automated accessibility check (for example Lighthouse) is run on the main pages and the result is recorded, with a target score of 90 or higher.
- The layout works on a phone-width screen (responsive) in the current versions of Chrome, Firefox, Edge and Safari.

### 6.4 Performance

- Summary within 60 seconds for text-based PDFs of up to 30 pages, and within 120 seconds for 31 to 50 pages (FR-8). Each Quiz is generated in under 60 seconds.
- Pages other than AI processing respond in under 2 seconds on a normal home or campus broadband connection.

### 6.5 Testing, Traceability and Repository

- Deterministic logic has automated tests (§5.5); the AI-dependent behaviour has the Test Set evaluation (§5.4).
- Traceability: each epic and story names the FR numbers it implements, and each automated test and each Test Set check names the FR or SM it verifies (in the test name or a comment). FR numbers are stable, so an examiner can follow a requirement from this PRD to a story, a test and the code.
- Documentation, test data and secrets have separate, documented places in the repository.
- The build order is: first the text-extraction check on a real PowerPoint export (FR-4), then the Summary, Multiple Choice, Fill-in-the-Gaps and Essay Feedback. A working app exists early and the most time is left for Essay Feedback.

### 6.6 Key Screens

The key screens and flows are listed here and sketched in the UX step (`bmad-ux`, which produces `DESIGN.md` and `EXPERIENCE.md`), not in this PRD:

- Register and log in.
- Upload (with the external-AI notice and the limits).
- Summary (Summary Parts with Source References, Key Terms, AI-generated notice).
- Quiz (one screen per type: Multiple Choice, Fill-in-the-Gaps, Essay with the answer field).
- Results with Essay Feedback and the Review List.
- Saved lectures and past Attempts.
- Demo Mode banner and the example Lecture.

## 7. Non-Goals (Explicit)

- Not a general chat with a PDF; there is no free prompt field.
- Not a replacement for reading the lecture or textbook; Recall helps students find out what they understood.
- Not a tool that grades students for courses; Essay Feedback is for the student's own learning and is not an official assessment.
- Not building a technical moat or custom AI model; it uses an existing AI service.
- Not a language-learning tool; feedback does not correct spelling or grammar.

## 8. MVP Scope

### 8.1 In Scope

- Registration and login, with private lectures and results (FR-1, FR-2).
- Upload of a single text-based PDF within limits, with the external-AI notice and a daily upload limit (FR-3 to FR-7).
- Plain-language Summary with Source References and Key Terms, and the AI-generated notice (FR-8 to FR-11).
- Quizzes in three formats (FR-12 to FR-17).
- Score and Review List (FR-18, FR-19).
- Saved lectures and results, and deletion (FR-20, FR-21).
- Report a wrong question (FR-22).
- Demo Mode and run-from-README (FR-23, FR-24).
- AI output quality checks (FR-25 to FR-31).

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

The lecturer asked for criteria that can be tested during the course, so every metric below is a test case. Launch metrics (active users, return rate, cost per user) are described under "Success Criteria" and "Vision" in `brief-recall.md` and are not v1 criteria. Requirements without a metric (for example FR-20 to FR-22, FR-31) are covered by the automated tests in §5.5 and the traceability rule in §6.5.

**Primary**
- **SM-1**: Summary speed — a text-based PDF of up to 30 pages gives a Summary in under 60 seconds, and one of 31 to 50 pages in under 120 seconds. Validates FR-8.
- **SM-2**: Source references — every Summary Part shows valid slide numbers and every Question links to a Summary Part (100 %, automatic). Validates FR-8, FR-12, FR-14, FR-16, FR-27.
- **SM-3**: Multiple choice — every question has four options with exactly one correct, and the score for a known set of answers is exactly right. Validates FR-12, FR-13.
- **SM-4**: Fill-in-the-gaps — the matching rules produce the expected result in all example tests in FR-15. Validates FR-15.
- **SM-5**: Essay feedback — on the Test Set, every good answer is rated above every weak answer; every weak answer's feedback names at least one missing key point; every misunderstanding answer is rated below every good answer and its feedback names the missing or wrong point; and the ranking holds in all three runs of each answer. Validates FR-17, FR-29.
- **SM-6**: Review list — every wrongly answered question leads to a Review List entry linked to the right Summary Part. Validates FR-19.
- **SM-7**: Accounts and access — a logged-out visitor, and one User asking for another's data, get no lecture data. Validates FR-1, FR-2.
- **SM-8**: Input limits — PDFs over 50 pages or 10 MB, non-PDF files and scanned PDFs are rejected with a clear message and make no AI call; a sixth upload on one day is rejected. Validates FR-3, FR-4, FR-7.
- **SM-9**: Runnable without keys — a fresh clone runs in Demo Mode from the README without keys, and the Demo Mode limits are shown. Validates FR-23, FR-24.

**Secondary**
- **SM-10**: AI output quality — on the Test Set, all of the following hold (FR-28): at least 80 % of Reference Key Points covered per Lecture; no unsupported statement in any Summary in the Test Set; at least 90 % of Questions grounded and 100 % with exactly one correct answer or expected term; 100 % of marked answer keys correct; 100 % of Source References valid and at least 90 % pointing to the right slides. Validates FR-28.
- **SM-11**: Prompt discipline — every Prompt change has an evaluation report from before and after. Validates FR-30.

**Counter-metrics (do not optimize)**
- **SM-C1**: Number of questions generated — more questions are not better; wrong or duplicate questions harm the student. Reading: the evaluation report lists the number of duplicate, wrong or unclear questions found per Lecture. Counterbalances SM-3, SM-10.
- **SM-C2**: Quiz score — a high score is not the goal and must never be raised by easier questions; the aim is for the student to see what they do not yet know. Reading: the builder compares the difficulty of questions before and after each Prompt change on the Test Set and records any drop. Counterbalances SM-5, SM-6.
- **SM-C3**: Summary length — a shorter Summary must not be reached by dropping Reference Key Points. Reading: the evaluation report shows the Summary length next to the key-point coverage, so a shorter Summary with lower coverage is visible. Counterbalances SM-1.

## 10. Open Questions

None of these blocks the UX or architecture steps. Each has an owner (the builder) and a condition for revisiting it.

1. Technology stack, AI service and storage are not chosen. They are decided in the architecture step, keeping to one web app with simple storage. A cost estimate (§6.2) is made once the AI service is chosen. *Revisit: when running the architecture step.*
2. Which three to five lectures make up the Test Set? None are chosen. At least one should be a real PowerPoint export. *Revisit: before the text-extraction check on a PowerPoint export (FR-4), which comes first in the build order.*
3. What is the deadline for the project? It is unknown, and it affects whether items under "If time" are realistic. *Revisit: when the epics are planned.*
4. The extracted-text threshold in FR-4 (100 characters per page) is a confirmed starting value, tuned with real slides early. *Revisit: after the first extraction check on real slides.*
5. The question counts in FR-12, FR-14 and FR-16 (10, 8 and 2) are confirmed starting values. *Revisit: after the first evaluation runs.*
6. The faithfulness target ("no unsupported statement in any Summary in the Test Set", FR-28, SM-10) is binary, "unsupported" is not defined (paraphrase? inference? omission?), and one reader judges it. A strict target may be hard to meet and may block Prompt changes (FR-30). Define "unsupported" and decide what happens if the target cannot be met. *Revisit: before the first evaluation run.*
7. The Essay Rating is a count of key points, and an Essay question needs only two (FR-16), so ratings take the values 0, 1 or 2 and good and weak answers may tie. Consider requiring three or more key points, and comparing the AI's reported covered points with the builder's pre-marked points exactly. *Revisit: when the Test Set essay questions are frozen (FR-26).*
8. Language-error insensitivity (FR-17) is not tested: the prepared answers are good, weak and misunderstanding, and none isolates spelling and grammar errors. Norwegian-language slides are supported (§4.3) but no Test Set Lecture is required to be in Norwegian. *Revisit: when the prepared answers are written (FR-29).*
9. No metric tests the thesis, that second-language students find the Summary easier to use, or the fifteen-minute claim (§5.7). Consider a timed walkthrough of UJ-1 by one or two second-language students. *Revisit: when the app can run the whole flow.*
10. All quality judgements in §5.4 are made by a single builder. This is a known limit of a solo project and is accepted in v1 (§5.7). *No revisit planned.*

Closed on 2026-10-06: the time bound for PDFs of 31 to 50 pages is 120 seconds (FR-8).

## 11. Confirmed Assumptions

*Every assumption made in the first draft. **The builder confirmed all of them on 2026-10-06**, with one change: the faithfulness target in FR-28 and SM-10 now reads "no unsupported statement in any Summary in the Test Set" (it first read "in most Summaries"). The summary language (the language of the slides) was also confirmed. The inline `[ASSUMPTION]` tags have been removed from the document; this list is the record of what was assumed. FR numbers below are the current ones; the review renumbered the FRs into reading order; the old-to-new mapping is in §12. Confirmations and changes are logged in `.memlog.md`.*

- **§2.1** — The second-language student is the only design driver; the busy student uses the same flow. *(Confirmed 2026-10-06.)*
- **§3 Glossary (Slide)** — One PDF page equals one slide. *(Confirmed 2026-10-06.)*
- **§3 Glossary (Essay Rating)** — The rating is a count of covered Reference Key Points. *(Confirmed 2026-10-06.)*
- **§4.1** — Email-and-password authentication with an established library; no email verification, no password reset. *(Confirmed 2026-10-06.)*
- **FR-4** — Scanned PDF threshold: fewer than 100 characters of text per page on average. *(Confirmed 2026-10-06.)*
- **FR-5** — On failure, an error and a retry button; no partial Summary. *(Confirmed 2026-10-06.)*
- **§4.3** — The Summary is in the language of the slides; the interface is English. *(Confirmed 2026-10-06.)*
- **FR-8** — The 60-second target is measured with the real AI service; Demo Mode is exempt. *(Confirmed 2026-10-06.)*
- **FR-10** — No automated readability score; plain language is judged by the builder. *(Confirmed 2026-10-06.)*
- **§4.4 / FR-12** — 10 Multiple Choice questions, generated once and stored; generation under 60 seconds. *(Confirmed 2026-10-06.)*
- **§4.5** — 8 Fill-in-the-Gaps questions, generated once and stored. *(Confirmed 2026-10-06.)*
- **FR-15** — "One wrong letter" means an edit distance of one. *(Confirmed 2026-10-06.)*
- **§4.6** — 2 Essay questions per Lecture, each with stored Reference Key Points. *(Confirmed 2026-10-06.)*
- **FR-17** — An empty or one-word answer gets the lowest rating and all key points listed as missing. *(Confirmed 2026-10-06.)*
- **FR-21** — A delete-lecture function is included as a privacy safeguard. *(Confirmed 2026-10-06.)*
- **FR-22** — No admin screen; the builder reads reports from the database or an export. *(Confirmed 2026-10-06.)*
- **FR-23** — Demo Mode offers prepared example answers with stored feedback; free-text essays need an API key. *(Confirmed 2026-10-06.)*
- **FR-26** — At least one Test Set Lecture is a real PowerPoint export. *(Confirmed 2026-10-06.)*
- **FR-27** — Two automatic retries on unusable AI output. *(Confirmed 2026-10-06.)*
- **FR-28 / SM-10** — The percentage targets (80 %, 90 %) are the builder's own and may be adjusted with a logged reason. *(Confirmed 2026-10-06.)*
- **FR-28 / SM-10 (changed on confirmation)** — The faithfulness target first read "no unsupported statements in most Summaries", which is not measurable. At the builder's request it now reads "no unsupported statement in any Summary in the Test Set". *(Changed and confirmed 2026-10-06.)*
- **FR-29** — Six prepared answers per essay question (two good, two weak, two misunderstanding); misunderstandings must rank below good answers; each answer is run three times. *(Confirmed 2026-10-06.)*
- **FR-30** — A Prompt change that breaks a previously passing check is rolled back or reworked. *(Confirmed 2026-10-06.)*
- **FR-31** — Report review is manual and occasional. *(Confirmed 2026-10-06.)*
- **§5.7** — The README includes a "what we checked and what we did not" section. *(Confirmed 2026-10-06.)*
- **FR-6 (was §6.1)** — A one-time notice on the upload page about external AI processing, acknowledged on first upload. *(Confirmed 2026-10-06.)*
- **FR-7 (was §6.2)** — 5 uploads per User per day. *(Confirmed 2026-10-06.)*
- **§6.3** — WCAG 2.1 AA as a target, with no formal audit. *(Confirmed 2026-10-06.)*
- **§6.4** — Pages other than AI processing respond in under 2 seconds. *(Confirmed 2026-10-06.)*
- **§8.2** — No email verification, password reset or admin screen in v1. *(Confirmed 2026-10-06.)*

### Added during the review pass (confirmed 2026-10-06)

These details were added while applying the review findings. The builder asked for the changes themselves, and the builder confirmed all the values below on 2026-10-06:

- **§6.3** — Browsers: current Chrome, Firefox, Edge and Safari. Accessibility check: an automated Lighthouse run on the main pages, target score 90 or higher.
- **FR-8, §6.4** — "Normal connection" means home or campus broadband.
- **FR-8, §6.4, SM-1** — PDFs of 31 to 50 pages: Summary in under 120 seconds, with a progress indicator. This is the builder's own decision.
- **FR-14, FR-16** — Fill-in-the-Gaps and Essay generation also under 60 seconds.
- **FR-6** — The notice is acknowledged once, before the first upload, and repeated in the README.
- **FR-10** — Question wording avoids double negatives and idioms, checked by the builder.
- **FR-23** — A visible Demo Mode banner on every page.
- **FR-26** — AI-generated Essay questions are also generated for each Test Set Lecture and checked for grounding, but are not used for the answer ranking.
- **FR-28** — The answer-key check covers every generated Multiple Choice and Fill-in-the-Gaps question for the Test Set Lectures.
- **§9** — The measurement readings for SM-C1 to SM-C3.
- **§6.2** — The advice to use a small, inexpensive model if the quality checks pass with it.

## 12. Review Changes (2026-10-06)

The FR numbers were renumbered into reading order after the reviewer pass. Old to new: FR-6 to FR-8, FR-7 to FR-9, FR-8 to FR-10, FR-9 to FR-12, FR-10 to FR-13, FR-11 to FR-14, FR-12 to FR-15, FR-13 to FR-16, FR-14 to FR-17, FR-15 to FR-18, FR-16 to FR-19, FR-17 to FR-20, FR-18 to FR-21, FR-19 to FR-22, FR-20 to FR-23, FR-21 to FR-24, FR-22 to FR-25, FR-24 to FR-26, FR-23 to FR-27, FR-29 to FR-11, FR-25 to FR-28, FR-26 to FR-29, FR-27 to FR-30, FR-28 to FR-31. FR-1 to FR-5 are unchanged. FR-6 (notice) and FR-7 (upload limit) are new FRs promoted from §6.1 and §6.2. SM-8 was split into SM-8 and SM-9; the later metrics moved up by one.

The review files in this folder (`review-rubric.md`, `reconcile-brief.md`, `reconcile-tilbakemelding.md`) were written before the renumbering and use the old FR numbers.
