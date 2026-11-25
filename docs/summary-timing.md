# Summary timing (SM-1, SM-2)

Manual test by the builder on **2026-11-25**, in the browser with a stopwatch, from pressing Upload until the page said Ready. Real key, free tier, `.venv/Scripts/python run.py`.

## Result

| Run | Model | Prompt version | PDF | Time to Ready | Outcome |
|---|---|---|---|---|---|
| Earlier the same day | `gemini-3.5-flash-lite` | v2 | test lecture | 11 seconds | Failed on a 503 from Google (before the longer retries) |
| Lecture 13 | `gemini-3.5-flash-lite` | v2 | test lecture | not Ready | **Failed**: repeated 503, also after the new retries (2, 5, 10 s) |
| Lecture 11 | `gemini-3.5-flash-lite` | v2 | test lecture | not Ready | **Failed**: repeated 503, also after the new retries (2, 5, 10 s) |
| Lecture 15 (user `tester4`) | `gemini-3.1-flash-lite` (the documented fallback, set in the builder's own `.env`) | v2 | own test lecture, 12 slides, text PDF | **8 seconds** | Ready; 5 parts, 7 key terms |
| Lecture 12, 14:04 (before the switch to the fallback) | `gemini-3.5-flash-lite` (default; `run.py` log: `models/gemini-3.5-flash-lite`, `result=ready`) | v2 | text-only journal PDF (article not named; page count not recorded) | 16 seconds | Ready |

Real Gemini calls: one request per successful upload. The failed runs used up to 4 requests each (1 try and 3 retries).

## Source check (SM-2)

`.venv/Scripts/python manage.py check_summary 15` gave: **OK: every Source Reference slide exists in the PDF** (12 pages stored, no AI call).

## Checked by the builder in the browser

The Summary page was read as a nurse would read it: the content was correct. "Jump to", the slide chips, the key terms and the AI notice all work, also in a narrow window.

## Findings

- **SM-1 was met in two runs**: the default model `gemini-3.5-flash-lite` made the journal PDF Ready in 16 s (lecture 12), and the fallback `gemini-3.1-flash-lite` made the test lecture Ready in 8 s (lecture 15). Both are under 60 s (text PDF of up to 30 pages).
- **The default model also failed that day**: it answered 503 repeatedly on the test lecture (lectures 13 and 11), even after 3 retries with waits of 2, 5 and 10 seconds. So the default worked once and failed on the test lecture; it is not reliable on the free tier at busy times. The default stays `gemini-3.5-flash-lite` in `config/settings.py`; the fallback is chosen with `GEMINI_MODEL` in the local `.env`.
- The time depends on Google's free-tier load on the day. A 503 streak is outside the app's control; the app fails the lecture calmly and the student can press Try again (at most 3 times).
- Not timed: PDFs of 31 to 50 pages (the test lectures have 10 to 12 slides).
- Only one test lecture (fallback) and one journal PDF (default) completed, so this is a small sample, and the two PDFs ran on different models.
