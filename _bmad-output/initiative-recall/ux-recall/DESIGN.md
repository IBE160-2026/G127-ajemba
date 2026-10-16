---
name: Recall
description: Calm, high-contrast, readable study app for students who study in a second language. Light mode only in v1.
status: final
created: 2026-10-16
updated: 2026-10-16
colors:
  surface-base: '#F5F6FB'
  surface-raised: '#FFFFFF'
  ink-primary: '#1B2033'
  ink-secondary: '#444B66'
  primary: '#3B4BA8'
  on-primary: '#FFFFFF'
  primary-soft: '#E2E6F7'
  border: '#A9B0D6'
  border-control: '#6B739E'
  success: '#1B6B3A'
  attention: '#A32D2D'
  focus: '#B36B00'
typography:
  body:
    fontFamily: "Verdana, 'Segoe UI', system-ui, sans-serif"
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.6
  body-large:
    fontFamily: "Verdana, 'Segoe UI', system-ui, sans-serif"
    fontSize: 22px
    fontWeight: 400
    lineHeight: 1.6
  body-xlarge:
    fontFamily: "Verdana, 'Segoe UI', system-ui, sans-serif"
    fontSize: 26px
    fontWeight: 400
    lineHeight: 1.6
  heading-1:
    fontFamily: "Verdana, 'Segoe UI', system-ui, sans-serif"
    fontSize: 28px
    fontWeight: 700
    lineHeight: 1.3
  heading-2:
    fontFamily: "Verdana, 'Segoe UI', system-ui, sans-serif"
    fontSize: 22px
    fontWeight: 700
    lineHeight: 1.4
  meta:
    fontFamily: "Verdana, 'Segoe UI', system-ui, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: 8px
  md: 12px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 24px
  '6': 32px
  '7': 48px
  content-max: 720px
  margin-mobile: 16px
components:
  button-primary:
    backgroundColor: '{colors.primary}'
    textColor: '{colors.on-primary}'
    typography: '{typography.body}'
    rounded: '{rounded.sm}'
    minHeight: 48px
  button-secondary:
    backgroundColor: '{colors.surface-raised}'
    textColor: '{colors.primary}'
    borderColor: '{colors.primary}'
    rounded: '{rounded.sm}'
    minHeight: 48px
  card:
    backgroundColor: '{colors.surface-raised}'
    rounded: '{rounded.md}'
    padding: '{spacing.5}'
  source-chip:
    backgroundColor: '{colors.primary-soft}'
    textColor: '{colors.ink-primary}'
    typography: '{typography.meta}'
    rounded: '{rounded.full}'
    minHeight: 44px
  answer-option:
    backgroundColor: '{colors.surface-raised}'
    borderColor: '{colors.border-control}'
    rounded: '{rounded.sm}'
    minHeight: 48px
  text-input:
    backgroundColor: '{colors.surface-raised}'
    textColor: '{colors.ink-primary}'
    borderColor: '{colors.border-control}'
    rounded: '{rounded.sm}'
    minHeight: 48px
---

## Brand & Style

Recall is a quiet study room, not an exam hall. The student has just left a lecture in a language that is not their own; the interface must lower effort, not add to it. The mood is calm and supportive: soft indigo on a pale surface, plenty of space, no pressure devices (no timers, no countdowns, no streaks, no red alarm signals).

Readability comes before style. Every visual decision is checked against one question: can a tired second-language reader read this without effort? Decoration is kept to a minimum. Clear and professional is the target, since this is a coursework project.

## Colors

- **Surface base (`{colors.surface-base}`)** is the page background, a very light indigo-tinted white that softens glare.
- **Surface raised (`{colors.surface-raised}`)** is white, for cards, inputs and answer options.
- **Ink primary (`{colors.ink-primary}`)** is all main text. Contrast on both surfaces is above 14:1.
- **Ink secondary (`{colors.ink-secondary}`)** is for labels and small notes. Contrast on both surfaces is above 7:1. Never lighter.
- **Primary (`{colors.primary}`)** is the only brand colour: main buttons, links, selected tabs, selected answer. White text on it is above 7:1.
- **Primary soft (`{colors.primary-soft}`)** is for selected backgrounds, source chips and the key terms panel.
- **Border (`{colors.border}`)** is a light outline for cards and dividers only. It is decorative and is never the only edge of a control (its contrast is about 2:1).
- **Border control (`{colors.border-control}`)** is the outline of every control: text inputs, the essay box, answer options and radio buttons. It has at least 3:1 contrast on all surfaces (4.6:1 on white, 4.3:1 on the page background, 3.7:1 on soft indigo), which meets the WCAG non-text contrast rule. Use 2px.
- **Success (`{colors.success}`)** and **Attention (`{colors.attention}`)** mark answer results. Both always come with an icon and a word. Attention is a deep red-brown used for "Not quite yet", never as a fill behind large areas, and never for the student's score.
- **Focus (`{colors.focus}`)** is a warm amber ring, 3px with a 2px offset, on every interactive element. It stands out from indigo.

Colour is never the only carrier of meaning. Dark mode is not in v1 (on the "if time" list in EXPERIENCE.md).

## Typography

One family: Verdana, then Segoe UI, then the system sans. Verdana is wide, with open letter shapes and clear differences between similar characters (I, l, 1), which helps readers who are decoding a second language. No web fonts are loaded, so there is no flash and no network cost.

- Body is 18px with line height 1.6. All reading text (summary, questions, answers, feedback, interface messages) uses body or larger.
- `meta` is 16px and is the smallest size allowed. It is used only for short supporting text: "Question 3 of 10", dates, status labels and source chips. Nothing smaller is used anywhere.
- The student can switch to large (22px) or extra large (26px). Every type token scales together, including `meta` and headings, keeping the same proportions.
- Lines are limited to about 70 characters (`{spacing.content-max}`).
- Left-aligned only. No justified text, no italics for content, no all-caps, no light weights.
- Bold is used for headings and key terms. Underline is used only for links.

## Layout & Spacing

Single column, centred, maximum width `{spacing.content-max}`. The Summary screen adds a key terms panel beside each part on wide screens (see EXPERIENCE.md); the whole layout is then up to 1040px.

Spacing scale: 4 / 8 / 12 / 16 / 24 / 32 / 48. Space between cards and sections is `{spacing.6}` or more. Inside cards the padding is `{spacing.5}`. On a phone the page margin is `{spacing.margin-mobile}`, the layout is one column, and nothing scrolls sideways except the tab row.

Touch and click targets are at least 48 by 48px with 8px between them. Source chips are links and are at least 44px tall.

The top bar wraps to a second row instead of overflowing, so nothing is cut off at 320px width or at the largest text size. Buttons and inputs grow in height when their label wraps; no control has a fixed height.

## Elevation & Depth

Flat. Cards are separated by a 1px `{colors.border}` outline and tone, not by shadows. Overlays are avoided; where one is needed (text size menu on phone) it has a 2px border.

## Shapes

`{rounded.sm}` (8px) for inputs, buttons and answer options. `{rounded.md}` (12px) for cards. `{rounded.full}` only for source chips and tabs. Corners are soft but not playful.

## Components

- **Button primary:** `{colors.primary}` fill, white text, label in `{typography.body}` bold, min height 48px. Always has a text label; an icon may sit before it. Disabled state uses `{colors.border}` outline and `{colors.ink-secondary}` text (not a faded fill) and explains why in a note.
- **Button secondary:** white fill, 2px `{colors.primary}` border, primary text.
- **Icon:** simple outline icon drawn as SVG (never emoji), 24px, always placed next to a visible text label. Never used alone. Icons carry no meaning that the label does not also carry.
- **Card:** white, 1px border, `{rounded.md}`, padding `{spacing.5}`. One idea per card.
- **Source chip:** pill with `{colors.primary-soft}` fill, 1px `{colors.border-control}` border, `{typography.meta}` text such as "Slides 12 to 15", minimum height 44px. It is a link to the summary part and looks like one (underlined text, arrow icon).
- **Key terms panel:** `{colors.primary-soft}` background card. Each term is bold, followed by one plain sentence.
- **Answer option (multiple choice):** full-width, min 48px tall, 2px `{colors.border-control}` border, radio control plus text. Selected: 2px `{colors.primary}` border, `{colors.primary-soft}` fill and a filled radio dot. After checking, the chosen and the correct options get a label ("Your answer", "Correct answer") and an icon.
- **Text input:** at least 48px tall, 2px `{colors.border-control}` border, label always visible above it (never placeholder-only). Error text sits under the field with an icon and starts with what to do.
- **Essay box:** multi-line input, at least 8 lines tall, same border and label rules.
- **Feedback block:** card with a heading and an icon (for example check mark for "What you explained well", dash for "What is missing", book for "Read this part again").
- **Tabs:** underlined text tabs on wide screens. On a phone they become a horizontally scrollable row with the same full labels (no short labels). The selected tab has a 3px `{colors.primary}` underline and bold text. An edge fade shows that the row scrolls.
- **Step list (processing):** vertical list of three steps; done = check icon, current = spinner-free "In progress" label, waiting = empty circle.
- **Notice banner:** `{colors.primary-soft}` fill, 2px `{colors.border-control}` border, icon plus text. Used for the AI notice and the demo banner. The demo banner is one short sentence plus a link, and is not dismissible.
- **Text size control:** three buttons labelled "A", "A+" and "A++" with the visible words "Text size" and the current level in text, shown in the top bar (or in the first row of the wrapped bar on a phone).

## Do's and Don'ts

**Do**
- Keep reading text at 18px or larger and supporting text at 16px or larger, with line height 1.6.
- Use `{colors.border-control}` for the edge of every control.
- Let controls grow in height; use minimum heights, never fixed heights.
- Use icon plus word, every time.
- Keep at least `{spacing.6}` between sections.
- Show a clear focus ring on everything that can be activated.
- Keep one primary button per screen area.

**Don't**
- Don't use colour alone to show correct, wrong, selected or current.
- Don't use red or large attention fills for answers or scores.
- Don't use animation other than a short fade (150ms). With "reduce motion" on, there are no animations at all.
- Don't use progress bars that imply a percentage the app does not know.
- Don't use timers, countdowns, streaks or badges.
- Don't use placeholder text as a label.
- Don't use emoji as icons.
- Don't use `{colors.border}` as the only edge of a control.
- Don't use all-caps, italics, justified text or text on images.
