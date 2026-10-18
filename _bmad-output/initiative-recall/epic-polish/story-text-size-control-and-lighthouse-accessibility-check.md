---
id: 1
type: story
title: "Text size control and Lighthouse accessibility check"
parent: epic-polish
after: [4.3]
refined: true
hitl: false
risk: low
---

# Text size control and Lighthouse accessibility check

## Description

The student can choose normal, large or extra large text and the choice is kept on that device. An automated Lighthouse accessibility check runs on the main pages, what it finds is fixed, and the result is recorded in `docs/`. This story delivers PRD §6.3 and owns no FR number.

## Acceptance Criteria

1. **The size choice is kept**
   **Given** the text-size control on every page
   **When** the student picks large and reloads or visits another page
   **Then** large is still applied from the start, with no flash of the old size
2. **Logout does not erase the choice**
   **Given** the choice stored in the browser under a key without the `recall:` prefix
   **When** the student logs out
   **Then** the choice stays (the logout cleanup removes only `recall:` keys)
3. **Accessibility basics hold**
   **Given** the main pages (login, upload, Summary, quiz, results)
   **When** they are used with the keyboard and with reduced motion on
   **Then** every control can be reached and used, icons have text labels, there are no timers, and animation is off
4. **Lighthouse is run and recorded**
   **Given** the main pages
   **When** Lighthouse accessibility runs
   **Then** each scores 90 or higher, and `docs/accessibility-results.md` records the scores, the date and what was fixed or listed as a known gap
5. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** an "Accessibility" section says how to change text size and links `docs/accessibility-results.md`

## Tests

- `test_readme_has_required_sections` (adds "Accessibility" to the list)
- `test_text_size_script_keeps_choice` (script logic where testable)
- `test_logout_cleanup_keeps_text_size_key`
- Manual: Lighthouse runs on five pages and a keyboard walk-through, recorded in `docs/`

## Boundaries

- Must not change: page behaviour. Only `static/js/app.js` holds the script; no inline scripts (AD-1, AD-19).

## References

- parent — _bmad-output/initiative-recall/epic-polish/epic-polish.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-1, AD-19.3, AD-22
- design — _bmad-output/initiative-recall/ux-recall/EXPERIENCE.md (Accessibility Floor, Responsive); review-accessibility.md
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, §6.3

## Notes

- Assumption: the key is `recall-textsize` (no colon) so the logout cleanup does not clear it.
