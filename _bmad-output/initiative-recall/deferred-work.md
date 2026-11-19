
- source_plan: `_bmad-output/initiative-recall/epic-upload-pdf-checks/story-upload-a-pdf-with-all-checks-plan.md`
  summary: Add the AD-20 memory cap to the PDF extraction subprocess.
  evidence: Only the 20 s limit is enforced; Windows has no portable per-process memory cap in the standard library (a Job Object or `resource` on Linux would be needed). A hostile PDF within 10 MB can use much memory for up to 20 s.
