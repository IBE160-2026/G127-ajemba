# Product Brief: Recall

## Executive Summary

Recall is a web app that turns lecture PDFs into a short summary of the key points and then tests the student's understanding with three types of questions: multiple choice, fill-in-the-gaps, and short essay questions with written feedback. A student uploads the slides from today's lecture and, within a minute, has a clear overview of what mattered and a quiz that shows what they actually understood.

Recall is designed first for students studying in a second language. Lecture slides are dense, fragmented, and written as speaking notes for the lecturer rather than as study material. For a student reading in a language that is not their own, this means extra time spent decoding the text before they can even begin to learn it. Many end up rereading slides passively, which feels productive but builds little understanding. Research on learning consistently shows that testing yourself (retrieval practice) is one of the most effective ways to learn, yet most students rarely do it because creating good questions is slow and hard.

The timing is right because AI models can now read a document and produce accurate summaries and varied questions in seconds, at a cost low enough for a student product. What was a teaching assistant's job a few years ago can now be done on demand for every lecture, every week.

## The Problem

A typical student has several courses running at once, each with weekly lecture slides of 30 to 60 pages. After a lecture, the slides sit in a folder until the week before the exam. By then, the student faces hundreds of pages and no clear idea of which parts they understand and which they only recognise.

How students cope today:

- **Rereading slides and highlighting.** Easy to do, but it creates a feeling of familiarity rather than real understanding. Students discover the gaps during the exam.
- **Writing their own summaries.** Effective but time-consuming, and students working part-time or with family responsibilities often cannot keep up.
- **Using generic AI chatbots.** Students paste text into a chatbot and ask for a summary. This works, but it requires knowing what to ask, gives inconsistent results, and rarely turns into structured self-testing.
- **Past exams and textbook questions.** Useful but limited, often not available for every topic, and not tied to what was actually covered in this year's lectures.

The cost of the status quo is wasted study hours, exam stress, and lower grades. It hits hardest for students who are studying alongside work, studying in a second language, or retaking a course, the people who have the least time and the most to lose.

## The Solution

Recall gives students a simple loop after every lecture: upload, understand, test.

1. Upload. The student logs in and uploads a lecture PDF.
2. Understand. The app produces a summary of the main highlights in plain language: the key concepts, definitions, and how they connect. Each part of the summary shows which slides it is based on, and key terms are listed with a short, simple explanation.
3. Test. The student chooses how to be tested:
- Multiple choice for quick checks of facts and concepts (recognition).
- Fill-in-the-gaps for key terms and definitions (recall).
- Essay questions for deeper understanding (explanation). The student writes a short answer and receives feedback on what they got right, what is missing, and which   part of the lecture to revisit.

After each quiz, the student sees a score and a short list of topics to review, each linked back to the relevant part of the summary. The student's lectures and results are saved to their account, so they can come back to them later. The outcome is that the student knows, in about fifteen minutes, what they understood from a lecture and where to spend their study time.

## What Makes This Different

Honestly, summarising and quiz tools already exist (for example Quizlet, NotebookLM, and various "chat with your PDF" apps), and there is no technical moat here. The same AI models are available to everyone. The difference lies in focus and design:

- **Built around the lecture, not the textbook or chat.** The product is designed for one specific job: "I just had a lecture, help me learn it." No prompting skills needed, no blank chat window.
- **Three levels of testing in one flow.** Many tools stop at flashcards or multiple choice. Including fill-in-the-gaps and essay questions with feedback moves the student from recognition to recall to explanation, which is how real understanding is built and how university exams actually test.
- **Feedback that points back to the source.** Every piece of feedback links to the part of the lecture it comes from, so the student can check the material rather than simply trusting the AI.
- **Designed by someone in the target group.** The builder is a working student in a Norwegian university programme and understands the day-to-day reality of the users. The realistic advantage is closeness to users and speed of iteration, not proprietary technology.

## Who This Serves

**Primary user: the university student studying in a second language. For example, an international student taking courses taught in Norwegian or English, neither of which is their first language. They follow the lectures but spend a long time decoding dense slides afterwards, and they are unsure whether they can explain the concepts in their own words. They need plain-language summaries, clear explanations of key terms, and a safe way to practise explaining what they have learned. Success for them means spending less time decoding and walking into an exam knowing which topics they can explain.

What this means for the design: plain language in summaries and feedback, key terms explained, short sentences, a clean and readable layout, and feedback on essay answers that focuses on content and understanding rather than penalising language mistakes.

**Secondary user: the busy university student. A student combining studies with work or family who needs a fast way to find out what they understood from a lecture. The same flow serves them well, since it is short and focused.

## Success Criteria

These criteria describe what the first version must do and can be checked with test cases during the course.

**Summary speed. A text-based PDF of up to 30 pages produces a summary in under 60 seconds.
**Source references. Every part of the summary shows which slide or page numbers it is based on, and every question links to the part of the summary it comes from.
**Multiple choice. Each multiple choice question has four options with exactly one correct answer, and the score after a quiz is calculated correctly.
**Fill-in-the-gaps. Answers that differ only in upper and lower case, extra spaces, or a single-letter typo are accepted as correct. Wrong words are marked as wrong.
**Essay feedback. For a fixed set of test answers, known good answers always receive a better assessment than known weak answers, and the feedback names at least one missing key point for every weak answer.
**Review list. After a quiz, every question answered wrongly leads to a topic in the review list, linked to the right part of the summary.
**Accounts and access. A user can register and log in, and only sees their own lectures and results. A logged-out user cannot access any saved lectures.
**Input limits and demo mode. PDFs over the size limit, or scanned PDFs without readable text, are rejected with a clear message. The app can be run in demo mode with a pre-processed example lecture, without an API key.

## How we check the quality of the AI's output

The AI produces the summaries, questions, and essay feedback, so its output must be checked, not trusted. We will build a small test set:

Fixed test lectures. Three to five lectures made from our own or freely licensed slides. For each one, we write down the key points in advance and check that the summary covers them and that the questions are based on them.
Known essay answers. For each test lecture, a set of prepared essay answers: some good, some weak, and some with typical misunderstandings. We check that the feedback ranks them correctly and points out what is missing (success criterion 5).
Versioned prompts. The prompts for summaries, questions, and essay feedback are stored as files in the repository, so changes can be tracked and the test set can be re-run after each change.
User reporting. A "report this question" button lets users flag wrong or unclear questions, which gives a way to find errors the test set misses.

## Scope

In the first version

User registration and login. Each user's lectures and results are private to their account.
Uploading a single text-based PDF, with a size limit (for example 50 pages or 10 MB).
An AI-generated plain-language summary with source references and explained key terms.
Quizzes in three formats: multiple choice, fill-in-the-gaps, and essay questions with written feedback.
A score and a list of topics to review after each quiz.
A simple way to report a wrong or unclear question.
A list of the user's saved lectures and quiz results.
A demo mode with a pre-processed example lecture, so the app can be tried without an API key.

Build order: summary, then multiple choice, then fill-in-the-gaps, then essay feedback. This gives a working app early and leaves the most time for the hardest part.

Explicitly out of the first version

Scanned or handwritten PDFs (these need text recognition and are less reliable).
Audio or video lecture recordings.
Sharing quizzes with classmates or study groups.
Integration with learning platforms such as Canvas.
Mobile apps (the first version is a responsive web app).
Payments and subscriptions.

If time (in priority order)

Spaced repetition: suggesting when to review topics the student got wrong.
An exam plan that combines all lectures in a course.
Flashcards generated from key terms.

Privacy and data

Lecture material and the student's answers are sent to an external AI service to be processed. This will be stated clearly in the app. Passwords will be handled with an established, well-documented authentication approach, never stored in plain text. API keys are kept out of Git (using a .env file, with a .env.example in the repository), and copyrighted course material is never added to the repository; test data uses our own or freely licensed slides.

## Vision

If Recall works, it becomes the place a student goes after every lecture, a personal study companion that knows everything they have covered in a course and what they still struggle with. In two to three years it could combine all the lectures in a course into an exam preparation plan, schedule reviews of weak topics at the right time, support audio and video recordings, and let study groups share and challenge each other with questions.

Signs of success after a real launch would include: a large share of users completing at least one quiz after uploading a lecture, users returning with new lectures over the semester, high ratings for summary accuracy, few reported question errors, and AI costs per user low enough for a sustainable student subscription.

Longer term, the same approach could serve professional learning, for example health workers or engineers who must keep up with new guidelines and prove they understand them. The core idea stays the same: turn learning material into understanding, and make it easy for people to find out what they actually know.
