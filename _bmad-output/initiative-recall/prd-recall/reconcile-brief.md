# Reconciliation: brief-recall.md vs prd-recall.md

Read-only comparison. Neither source file was modified. Overall: the PRD carries nearly all brief content faithfully; gaps are mostly qualitative or long-term signals.

## Gaps (dropped or weakened)

1. **Design implications for second-language users are scattered, not stated as design requirements.**
   Brief (Who This Serves): "plain language in summaries AND feedback, key terms explained, short sentences, clean and readable layout, feedback focused on content not language mistakes."
   PRD: summary plain language is FR-8 (prompt instruction only, builder-judged); interface plain language is in 6.3; no-language-penalty is in FR-14. But there is no plain-language requirement for essay feedback or question text, and no "clean and readable layout" requirement (6.3 covers WCAG and responsive only). Also the brief's point that essay questions let students "practise explaining concepts in the course language" is not stated in the PRD.

2. **Vision / long-term signals dropped.**
   Brief Vision: personal study companion across a course; 2-3 year ideas (exam plan, scheduled reviews, audio/video, study groups); signs of success after launch (share completing a quiz, returning users, summary accuracy ratings, few reported errors, AI cost per user for a sustainable subscription); longer-term professional learning (health workers, engineers).
   PRD: Section 9 only says launch metrics "belong to the brief"; PRD Vision (section 1) has no future direction at all. No pointer to professional learning or companion idea.

3. **Problem/status-quo context and "why now" lost.**
   Brief: coping strategies (rereading, own summaries, generic chatbots, past exams), cost of status quo (wasted hours, stress, lower grades), the "student recognises a term but cannot explain it in own words" insight, and the why-now (AI cost/speed makes a TA's job on demand).
   PRD: only a short version in section 1 and JTBD; chatbot-alternative comparison, part-time/family constraints and "why now" are gone. The "Designed by someone in the target group / closeness to users and speed of iteration" differentiator is also absent (PRD says only "no technical moat").

4. **Weakened or changed specifics.**
   - Brief says the app is "simple loop: upload, understand, test" and each quiz result shows "a short list of topics to review"; PRD preserves this (FR-16) but adds de-duplication per Summary Part, a mild refinement, not a contradiction.
   - Brief criterion "feedback links back to source" for every piece of feedback: PRD FR-29 covers it, OK.
   - Brief demo mode: "pre-processed example lecture without API key"; PRD adds prepared-answer essays only (a narrowing: free-text essays unavailable in demo). Disclosed in FR-20, so not hidden.
   - Brief "Review list ... every question answered wrongly leads to a topic": PRD merges multiple wrong answers into one entry and Essay entries; consistent in spirit.
   - Brief secondary user ("busy student") served by the same flow: PRD keeps this but demotes it explicitly; fine.

5. **Items preserved (no action):** build order (6.5), "if time" list and its priority order (8.2), out-of-scope list (8.2), privacy statements (6.1; passwords, .env, copyright), quality-check approach (section 5, expanded), 60 s / 50 pages / 10 MB limits, fill-in-gaps rules, essay ranking criterion, report-question button, demo mode, accounts.

## Contradictions
None found. Minor drift: brief says upload-to-summary "within a minute" generally; PRD narrows to under 60 s for up to 30 pages (matches brief criterion).

## Suggested fixes (not applied)
- Add a short design-principles list under 2 or 6.3: plain language in summaries, questions and feedback; short sentences; readable layout; content-focused essay feedback.
- Add a brief "Long-term vision" paragraph and a note that launch signals live in the brief.
- Restore the "closeness to users / speed of iteration" differentiator and one line on how students cope today.
