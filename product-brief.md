# Product Brief: StudyLens

## Executive Summary

Recall is a web app that turns lecture PDFs into a short summary of the key points and then tests the student's understanding with three types of questions: multiple choice, fill-in-the-gaps, and short essay questions with written feedback. A student uploads the slides from today's lecture and, within a minute, has a clear overview of what mattered and a quiz that shows what they actually understood.

The problem it solves is familiar to every university student. Lecture slides are dense, fragmented, and written as speaking notes for the lecturer rather than as study material. Students either reread them passively, which feels productive but builds little understanding, or they spend hours making their own summaries and practice questions before they can even start studying. Research on learning consistently shows that testing yourself (retrieval practice) is one of the most effective ways to learn, yet most students rarely do it because creating good questions is slow and hard.

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

1. **Upload.** The student uploads a lecture PDF.
2. **Understand.** The app produces a summary of the main highlights: the key concepts, definitions, and how they connect, in plain language and at a length that can be read in a few minutes.
3. **Test.** The student chooses how to be tested:
   - **Multiple choice** for quick checks of facts and concepts.
   - **Fill-in-the-gaps** for key terms and definitions, which requires recall rather than recognition.
   - **Essay questions** for deeper understanding. The student writes a short answer and receives feedback on what they got right, what is missing, and which part of the lecture to revisit.

After each quiz, the student sees a score and a short list of topics to review, each linked back to the relevant part of the summary. The outcome is that the student knows, in about fifteen minutes, what they understood from a lecture and where to spend their study time.

## What Makes This Different

Honestly, summarising and quiz tools already exist (for example Quizlet, NotebookLM, and various "chat with your PDF" apps), and there is no technical moat here. The same AI models are available to everyone. The difference lies in focus and design:

- **Built around the lecture, not the textbook or chat.** The product is designed for one specific job: "I just had a lecture, help me learn it." No prompting skills needed, no blank chat window.
- **Three levels of testing in one flow.** Many tools stop at flashcards or multiple choice. Including fill-in-the-gaps and essay questions with feedback moves the student from recognition to recall to explanation, which is how real understanding is built and how university exams actually test.
- **Feedback that points back to the source.** Every piece of feedback links to the part of the lecture it comes from, so the student can check the material rather than simply trusting the AI.
- **Designed by someone in the target group.** The builder is a working student in a Norwegian university programme and understands the day-to-day reality of the users. The realistic advantage is closeness to users and speed of iteration, not proprietary technology.

## Who This Serves

**Primary user: the busy university student.** For example, a student taking three courses while working part-time. They attend lectures (or watch recordings) but have little time to process the material afterwards. They need a quick way to find out what they understood and what they didn't, without spending an evening making their own notes. Success for them means walking into an exam knowing which topics they have mastered, and spending less total time to get there.

**Primary user: students studying in a second language.** International students often understand the content but lose time decoding dense slide text. A plain-language summary lowers the barrier, and the questions help them practise explaining concepts in the course language.

**Secondary user: lecturers and teaching assistants (later).** They could use the app to quickly generate practice questions for their own slides. This is not a focus for the first version.

## Success Criteria

**User success signals**

- At least 60% of users who upload a PDF complete at least one quiz.
- At least 40% of users return and upload a second lecture within two weeks.
- In a short in-app survey, at least 70% of users rate the summaries as accurate and useful (4 or 5 out of 5).
- Users report fewer than 1 in 20 questions as wrong or confusing, using a "report this question" button.
- Average time from upload to finished summary is under 60 seconds.

**Business and project objectives**

- 50 active student users during a first test period of one semester.
- Qualitative feedback from at least 10 students through short interviews, used to decide what to build next.
- Cost of AI usage per user per month stays low enough that a small student subscription (or free tier with limits) would be sustainable.

## Scope

**In the first version**

- Uploading a single text-based PDF (for example lecture slides exported from PowerPoint).
- An AI-generated summary of the main highlights.
- Quizzes in three formats: multiple choice, fill-in-the-gaps, and essay questions with written feedback.
- A score and a list of topics to review after each quiz.
- A simple way to report a wrong or unclear question.
- A basic list of the student's uploaded lectures so they can return to them.

**Explicitly out of the first version**

- Scanned or handwritten PDFs (these need text recognition and are less reliable).
- Audio or video lecture recordings.
- Flashcards and spaced-repetition scheduling.
- Sharing quizzes with classmates or study groups.
- Integration with learning platforms such as Canvas.
- Mobile apps (the first version is a responsive web app).
- Payments and subscriptions.

## Vision

If Recall works, it becomes the place a student goes after every lecture, a personal study companion that knows everything they have covered in a course and what they still struggle with. In two to three years it could combine all the lectures in a course into an exam preparation plan, schedule reviews of weak topics at the right time, support audio and video recordings, and let study groups share and challenge each other with questions.

Longer term, the same approach could serve professional learning, for example health workers or engineers who must keep up with new guidelines and prove they understand them. The core idea stays the same: turn learning material into understanding, and make it easy for people to find out what they actually know.
