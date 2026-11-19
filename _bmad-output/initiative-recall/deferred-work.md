
- source_plan: `_bmad-output/initiative-recall/epic-upload-pdf-checks/story-upload-a-pdf-with-all-checks-plan.md`
  summary: Add the AD-20 memory cap to the PDF extraction subprocess.
  evidence: Only the 20 s limit is enforced; Windows has no portable per-process memory cap in the standard library (a Job Object or `resource` on Linux would be needed). A hostile PDF within 10 MB can use much memory for up to 20 s.

- source_plan: `_bmad-output/initiative-recall/epic-upload-pdf-checks/story-upload-notice-acknowledgement-and-daily-limit-plan.md`
  summary: Changing `LIMIT_TIME_ZONE` on a running app can let one extra upload through, or block one, around the change.
  evidence: `UploadLog.local_day` is stored in the zone active at upload time and is compared with "today" in the new zone, so the same real day can be counted twice or not at all. Operator-only edge case found by the story 2.3 review; a fix (store UTC bounds, or recompute `local_day`) adds complexity. Limit raised or lowered through `UPLOADS_PER_DAY` works correctly.
