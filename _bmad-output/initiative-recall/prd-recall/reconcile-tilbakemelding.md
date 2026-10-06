# Reconciliation: lecturer feedback vs PRD

- **Input:** `tilbakemelding-product-brief.md` (lecturer feedback, Norwegian)
- **PRD checked:** `prd-recall.md` (first draft, before the review changes)
- **Source:** written from the reconciliation subagent's summary. The subagent could not write the file itself, so this file holds the summary, not its full item-by-item extract.

About 30 feedback items were checked. Most are covered, 5 were partly covered and 1 was missing.

## Covered

Testable success criteria; the dedicated section on checking the AI's output (including essay feedback calibration and fixed test lectures); one product name (Recall); login clarified; one primary user; Demo Mode, `.env.example` and a test PDF; PDF size limit; versioned prompts; accessibility for second-language students; privacy note; "if time" list; build order.

## Gaps found

1. **Key screens and flows not sketched (partial).** The PRD had only the UJ-1 narrative, with no screen list and no note that sketches are planned for the UX step.
2. **No cost plan (partial).** There were page, size and upload limits, stored sample responses and Demo Mode, but no cost estimate. The cost of repeated evaluation runs (each essay answer assessed three times) was not addressed.
3. **Real PowerPoint test not tied to the build order (partial).** A real PowerPoint export was required in the Test Set and the extraction threshold was "tuned early", but nothing made this an early milestone before the Summary build.
4. **Traceability and brief history (partial/missing).** The PRD cross-referenced FRs, SMs and UJs, but had no plan to carry FR numbers into stories and code. The lecturer's request to update the brief so the repository history shows how the plan developed was not mentioned in the PRD.
5. **Business goals not in the Vision (partial, minor).** §9 said usage goals belong to the brief's long-term vision, but §1 did not mention them.

## How each gap was handled in the PRD (2026-10-06)

1. A key screen list was added (§6.6), with sketches deferred to the UX step (`bmad-ux`).
2. A short cost note was added (§6.2); a cost estimate is an open question until the AI service is chosen (§10).
3. FR-4 now requires text extraction on a real PowerPoint export before the Summary is built, and the build order in §6.5 starts with it.
4. §6.5 adds a traceability rule (stories and tests name FR numbers); §0 notes that the brief was revised after the feedback and that the repository history shows it.
5. §1 and §9 now refer to `brief-recall.md` for the long-term vision and the launch metrics.
