# 06 Quiz: multiple choice

Reached from: the "Multiple choice" tab. Phone: the tab row scrolls with the full labels. Leads to: next question, then Results.

## Before checking

```
+--------------------------------------------------------------------------+
| Recall   My lectures   Upload      Text size: [A] [A+] [A++]   Log out    |
+--------------------------------------------------------------------------+
|  Databases: Normalisation                                                |
|  Summary │ Multiple choice │ Fill in the gaps │ Essay │ Results           |
|           ═════════════════                                              |
|  (i) These questions were made by AI. They can contain mistakes.         |
|                                                                          |
|  Question 3 of 10                                                        |
|  +--------------------------------------------------------------------+  |
|  |  What is an update anomaly?                                        |  |
|  |                                                                    |  |
|  |  ( ) A. A table has too many columns                               |  |
|  |  (•) B. The same fact is stored twice and one copy is not changed  |  |
|  |  ( ) C. A key is missing from a table                              |  |
|  |  ( ) D. A table has no name                                        |  |
|  |                                                                    |  |
|  |  [ ✓ Check answer ]        Skip question                           |  |
|  +--------------------------------------------------------------------+  |
|  Report this question                                                    |
+--------------------------------------------------------------------------+
```

"Check answer" is disabled until an option is chosen. Text beside it: "Choose one answer first."

## After checking (not correct)

```
|  +--------------------------------------------------------------------+  |
|  |  What is an update anomaly?                                        |  |
|  |                                                                    |  |
|  |  (•) A. A table has too many columns            – Your answer      |  |
|  |  ( ) B. The same fact is stored twice and one   ✓ Correct answer   |  |
|  |         copy is not changed                                        |  |
|  |  ( ) C. A key is missing from a table                              |  |
|  |  ( ) D. A table has no name                                        |  |
|  |                                                                    |  |
|  |  (i) Not correct yet. The correct answer is B.                     |  |
|  |      Read why: <Slides 12 to 15>                                   |  |
|  |                                                                    |  |
|  |  [ Next question → ]                                               |  |
|  +--------------------------------------------------------------------+  |
```

When correct: "✓ Correct." with the same layout and the source chip.

## Last question

The button reads "See your results" and opens the Results tab.

## Phone

Same card, options full width, buttons full width and stacked. Tab row scrolls sideways.

## Notes
- The answer is checked at once and cannot be changed afterwards.
- No timer, no auto-advance. "Question 3 of 10" is text only, no bar.
- Result is shown with icon and words, not colour alone. No red fill.
- A "Back" link shows earlier questions read-only.
- Progress is saved when the student changes tab or leaves.
- "Skip question" counts as not answered, adds the question to the review list, and moves to the next question.
- Focus moves to the result line after "Check answer". The options are in a `fieldset` with the question as `legend`.
