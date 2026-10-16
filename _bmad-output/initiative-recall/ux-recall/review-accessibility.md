# Accessibility review: Recall UX (2026-10-16)

Scope: `DESIGN.md`, `EXPERIENCE.md`, `wireframes/01–09`. Target: WCAG 2.1 AA (PRD §6.3), with a few 2.2 criteria noted. This is a review of the design documents, not of a built app. Nothing in the spines or wireframes has been changed. Contrast ratios were calculated from the token hex values.

## Contrast check of the tokens

| Pair | Ratio | Needed | Result |
|---|---|---|---|
| ink on surface-base / raised / primary-soft | 14.96 / 16.14 / 12.99 | 4.5 | Pass |
| ink-secondary on base / raised / primary-soft | 7.96 / 8.59 / 6.91 | 4.5 | Pass |
| primary on base / raised / primary-soft | 7.06 / 7.61 / 6.13 | 4.5 | Pass |
| on-primary (white) on primary | 7.61 | 4.5 | Pass |
| success on raised / base / soft | 6.54 / 6.06 / 5.26 | 4.5 | Pass |
| attention on raised / base / soft | 7.07 / 6.55 / 5.69 | 4.5 | Pass |
| focus ring on base / raised / soft | 3.88 / 4.18 / 3.37 | 3 | Pass |
| **border on base / raised / soft** | **1.97 / 2.13 / 1.71** | **3** | **Fail** |

## Findings (most serious first)

### A1. Input and answer-option borders fail the 3:1 non-text contrast rule — High
`{colors.border}` (#A9B0D6) is 2.13:1 on white. `DESIGN.md` says "Input borders use 2px so they meet the 3:1 non-text contrast rule", but thickness does not change contrast. This affects text inputs, the essay box, unselected answer options, cards-as-controls and radio outlines. WCAG 1.4.11.
**Fix:** add a darker `border-control` token of at least 3:1 on white and on surface-base (for example `#6B739E`, about 4.4:1) for every control boundary. Keep the light `border` only for decorative card outlines. Correct the sentence in DESIGN.md.

### A2. Fixed heights will clip text at large text sizes — High
`button-primary`, `button-secondary` and `text-input` use `height: 48px`. At "Extra large" (26px) or with labels such as "Upload and make summary" that wrap, a fixed height clips or overflows. WCAG 1.4.4, 1.4.12.
**Fix:** use `minHeight: 48px` for all of them (as `answer-option` already does), and say that buttons wrap their labels.

### A3. Top bar will not fit at 320px with large text — High
EXPERIENCE.md keeps the three-button "Text size" control visible next to the "Menu" button on a phone. At 26px text in a 320px viewport, logo + Menu + "Text size [A] [A+] [A++]" cannot fit on one row. WCAG 1.4.10 Reflow.
**Fix:** let the top bar wrap to two rows, or put "Text size" as the first item inside the Menu while keeping a visible "Text size" text link. State the rule that the bar wraps instead of overflowing.

### A4. Link and button names are ambiguous when repeated — Medium
- My lectures: every row has "Open" and "Delete". The review list has "Read this part →", the results card has several "Start again". A screen-reader user hears the same name many times. WCAG 2.4.4, 2.4.6.
- Source chips read "Slides 12 to 15" without saying where they lead.
**Fix:** accessible names include the object: "Open Databases: Normalisation", "Delete Databases: Normalisation", "Read this part again: Update anomalies", "Start multiple choice again", "Slides 12 to 15, Why we normalise". The visible text can stay short as long as the accessible name starts with the visible text (WCAG 2.5.3).

### A5. Stated 18px minimum is contradicted by the 15px `meta` style — Medium
DESIGN.md says 18px is the minimum "anywhere that carries content", but `meta` (15px) is used for "Question 3 of 10", source chips, status text and dates. It is also not stated whether `meta` and headings scale with the text size control.
**Fix:** raise `meta` to at least 16px (preferably 18px for chips and progress text), and state that all type tokens scale together at the three text sizes.

### A6. Session expiry or connection loss could lose an essay answer — Medium
EXPERIENCE.md keeps typed answers on a connection error, and keeps quiz progress with the account, but does not say what happens if the login session ends while the student writes an essay. WCAG 2.2.5 (AAA) and good practice for slow writers in a second language.
**Fix:** autosave the essay draft as it is typed (stored with the account, and in the browser as backup), and when a session ends, return to the same question after login.

### A7. Plain-language rule is broken by some of the interface text — Medium
The voice rules ban idioms, but some examples are hard for second-language readers:
- "Not quite yet." ("quite" and "yet" carry subtle meaning).
- "Well done." (an idiom).
- The upload notice "Do not upload files you are not allowed to share" is a double negative, which FR-10 avoids in questions.
- The phone tab labels "Choice" and "Gaps" are short but unclear.
**Fix:**
- "Not quite yet." → "Not correct yet."
- "Correct. Well done." → "Correct."
- "Only upload files you are allowed to share."
- Phone tabs: let the row scroll with the full labels ("Multiple choice", "Fill in the gaps") instead of short labels.

### A8. Tab and page structure details are missing — Medium
- It is not said whether each tab has its own URL. Without it, the browser Back button leaves the lecture, and the page title does not change. WCAG 2.4.2, 3.2.3.
- The scrollable phone tab row must be reachable by keyboard and must scroll the focused tab into view. The edge fade is visual only.
**Fix:** one URL per tab (for example `/lecture/12/summary`, `/quiz/choice`), unique `<title>` per screen ("Summary – Databases: Normalisation – Recall"), and focus scrolling for the tab row.

### A9. Feedback after "Check answer" may be announced twice — Low
EXPERIENCE.md both moves focus to the feedback card and announces the result through a polite live region. Many screen readers will read it twice, and the "Check answer" button disappears under focus.
**Fix:** choose one: move focus to the result heading (preferred, it also helps keyboard users) and do not use a live region for it.

### A10. Status changes in the lecture list — Low
"Processing…" turns into "Ready" or "Failed" while the student stays on My lectures. How the update arrives is not specified. WCAG 4.1.3, 2.2.2.
**Fix:** update the row text in place (no page reload, no moving content), announce it politely, and keep focus where it is.

### A11. Control semantics to state explicitly — Low
- Multiple choice: use `fieldset` and `legend` (the question), not only a visible label.
- Text size control: a button group with `aria-pressed`, with the group named "Text size".
- Earlier essay attempts: disclosure buttons with `aria-expanded`.
- Delete dialog: trap focus, close on Escape, return focus to the Delete button, `role="alertdialog"`.
- Essay box: hint linked with `aria-describedby`; attempt count included in the button name ("Get feedback again, attempt 2 of 3").
- Fill-in-the-gaps input: `spellcheck="false"` and `autocomplete="off"` so browser tools do not give hints; essay box keeps normal spellcheck.

### A12. Source chips may be too small to hit — Low
The chip is a pill in 15px text with no stated size. WCAG 2.2 target size (2.5.8) needs 24px; the PRD aims for 48px.
**Fix:** `minHeight: 44px` for chips (they are links), with 8px space between them.

### A13. Demo banner is long and persistent — Low
The banner is four sentences, cannot be closed, and sits on every page. At extra large text it could fill a phone screen. WCAG 1.4.10.
**Fix:** shorten it to one sentence ("Demo mode: you see an example lecture. Essay feedback is prepared.") with a link "What can I not do?" to the rest.

### A14. Emoji icons in the wireframes — Low
The wireframes use emoji (📄 🗑 📖 ⬆). Emoji look different on each device and may be read aloud.
**Fix:** state that real icons are SVG, `aria-hidden`, next to the visible label. The wireframes are only sketches, so no change is needed there except a note in the README legend.

### A15. Test plan covers only automated and keyboard checks — Low
PRD §6.3 and EXPERIENCE.md name a Lighthouse score and a keyboard pass. Automated tools find only part of the problems.
**Fix:** add a screen-reader pass (NVDA with Firefox or Chrome, VoiceOver on Safari) on the three core flows, a 200% zoom and 320px reflow check, and a check at "Extra large" text size. Record the result next to the Lighthouse result.

## What already works well

- Colour is never the only carrier: results use icon plus words, selected answers use a border, a fill and a radio dot.
- No timers, no auto-advance, no time limits (WCAG 2.2.1).
- Reduced motion is respected; the only animation is a 150ms fade.
- Visible labels on all fields, with errors next to the field in plain words (3.3.1, 3.3.2).
- Password paste allowed and "Show password" provided (WCAG 2.2 3.3.8).
- Skip link, landmarks, one `h1`, language attributes for lecture content (1.3.1, 2.4.1, 3.1.2).
- Text size control, Verdana at 18px, line height 1.6, 70-character line length.
- 48px targets with 8px gaps, visible focus ring that passes 3:1 against all surfaces.

## Not an accessibility issue, but found during the review

- **Key points count:** after today's PRD change (at least 3 Reference Key Points per essay), `EXPERIENCE.md` (Amara's flow, step 8–9) and `wireframes/08` and `09` still say "of 2 points / 2 key points". They should say 3.
- **Open items list:** `EXPERIENCE.md` "Open Items and PRD Follow-ups" items 1 to 7 are now done in the PRD (see PRD section 13). The list should be shortened to a pointer.
- **Skip question on fill in the gaps:** wireframe 07 has no "Skip question" link; the PRD change applies it to multiple choice (FR-13) and the review list for both types (FR-19). Decide whether fill in the gaps also gets "Skip question".

## Resolution (2026-10-16)

All 15 findings were applied to `DESIGN.md`, `EXPERIENCE.md` and the wireframes. The builder asked for the key-point count of 3 and "Skip question" in both quiz types in the same pass.

| # | Where fixed |
|---|---|
| A1 | `DESIGN.md`: new `border-control` token (#6B739E, 3.7 to 4.6:1), used by inputs, essay box, answer options, chips, notice banner |
| A2 | `DESIGN.md`: `minHeight` for buttons and inputs, layout rule "no fixed heights" |
| A3 | `DESIGN.md` Layout and `EXPERIENCE.md` IA and Responsive: top bar wraps to two rows |
| A4 | `EXPERIENCE.md` Accessibility Floor: unique accessible names; wireframes 02, 05, 09 notes |
| A5 | `DESIGN.md`: `meta` is 16px, smallest allowed; all type tokens scale together |
| A6 | `EXPERIENCE.md` Essay behaviour: draft saved while typing, restored after session end |
| A7 | "Not correct yet", "Correct.", "Only upload files you are allowed to share.", full tab labels on phone; wireframes updated |
| A8 | `EXPERIENCE.md` IA: one page address and one page title per tab |
| A9 | `EXPERIENCE.md` Interaction Primitives: focus moves to the result line, no live region for it |
| A10 | `EXPERIENCE.md` Lecture row: status changes in place, announced politely |
| A11 | `EXPERIENCE.md` Component Patterns: fieldset/legend, aria-pressed, aria-expanded, alertdialog, aria-describedby, spellcheck off for the gap input |
| A12 | `DESIGN.md`: source chip `minHeight: 44px` |
| A13 | `EXPERIENCE.md` State Patterns and `DESIGN.md`: one-sentence demo banner with a "What is different in demo mode?" link |
| A14 | `DESIGN.md` Icon and `wireframes/README.md`: SVG, never emoji |
| A15 | `EXPERIENCE.md` Accessibility Floor: screen-reader pass, 200% zoom, 320px reflow, "Extra large" text check |

Also fixed: "of 2 points" is now "of 3 points" everywhere, and "Skip question" is in both multiple choice and fill in the gaps.
