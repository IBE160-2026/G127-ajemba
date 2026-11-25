---
title: 'Checkpoint 3.5: compare real hours with estimates and adjust the cut'
type: 'chore'
ticket: '5'
created: '2026-11-25'
status: 'built'
baseline_revision: '55c2e4461cd20104a6a6331d47f1d62f0218dc6c'
route: 'oneshot'
route_source: 'auto'
risk: 'low'
review: 'none'
review_source: 'pinned'
lenses_ran: []
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Epics 1 to 3 (10 stories) were planned at 20 hours and took about 15. The builder must decide the cut of the remaining work before the deadline of 15 December 2026 (about 2 hours a day).

**Approach:** Record the builder's decision in documents only; no app code changes. Cut: epics 7 and 8 dropped (multiple choice only); milestone 6 evaluates only test lecture 1; epics 9 then 10 stay "if time". Remaining: milestones 4 to 6 (8 stories, ~16 h), own parts of milestone 6 (~2 h), hand-in checks (~2 h), report (~8 h).

**Always:** Date the entries 2026-11-25. Show git diff for each changed file. Never run git add, git commit or git push.

**Never:** Touch app code, tests, `.env`, or finished stories. No invented per-story hours.

</frozen-after-approval>

## Implementation Notes

Oneshot: documents only. Files: `initiative-recall.md` (Decision), PRD §16 (change log), `epic-evaluation.md` (Notes), `README.md` ("What we checked and what we did not"), `CLAUDE.md` (no-git rule). The commit step of the workflow is skipped by the builder's rule.

## Verification

**Commands:**
- `.venv/Scripts/python manage.py test` -- expected: all tests pass
- `uv run _bmad/method/scripts/tickets.py --project-root . next` -- expected: no errors
