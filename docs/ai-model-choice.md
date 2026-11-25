# AI model choice (story 3.1, FR-25)

Checked on **2026-11-25**. The model name is a setting (`GEMINI_MODEL`), never written in code.

## Choice

- **Model:** `gemini-3.5-flash-lite`
- **Documented fallback:** `gemini-3.1-flash-lite`. It was **not** tested in this spike, because the first model worked. Switching is a change of the `GEMINI_MODEL` setting only. Run the spike again first (see below).
- **Structured-output style that works:** `response_json_schema` with a JSON Schema (made from a Pydantic class with `model_json_schema()`) together with `response_mime_type="application/json"`. The answer is then checked with Pydantic.
- **Not decided:** the Pydantic-class style (`response_schema=<class>`) was tried once and got a 503 from Google, so it is neither proven nor rejected. It is not used.

## Free-tier limits seen

Read by the builder on the own AI Studio rate-limit page on 2026-11-25 (not measured by the code):

| Model | Requests per minute | Tokens per minute | Requests per day |
| --- | --- | --- | --- |
| Gemini 3.5 Flash Lite | 15 | 250K | 500 |
| Gemini 3.1 Flash Lite | 15 | 250K | 500 |

Other text models on the same page have only 20 requests per day, so they are not used. The key's own model list (SDK `models.list`, names only) shows `gemini-3.5-flash-lite` and `gemini-3.1-flash-lite` as available for `generateContent`.

## The two spike calls

Input: only `evaluation/testset/test-lecture-1.pdf` (the builder's own lecture, 12 slides). Script: `evaluation/spike_gemini.py`. Each call wrote one `AiCallLog` row (no content).

| # | Style | Result | Time | Tokens in / out |
| --- | --- | --- | --- | --- |
| 1 | `response_json_schema` | Worked (HTTP 200). Valid JSON: 5 summary parts with slide numbers 1 to 12, 4 key terms. | 2.3 s | 1248 / 547 |
| 2 | `response_schema` (Pydantic class) | Failed: `ServerError 503` (service unavailable). Not a problem with the style. | 1.5 s | 0 / 0 |

## What the 503 means for the code

The free tier can be unavailable for a short time. `ai_client.py` handles 503 and 429 calmly: one short wait and one retry, then a clear error that the job turns into the plain message of FR-5. A 429 whose text says `limit: 0` is not retried. No message, log line or error text contains the key.

## Run the spike again

`.venv/Scripts/python evaluation/spike_gemini.py <user email> <model> json_schema` (needs `GEMINI_API_KEY` in the local `.env`; sends the test lecture and writes one `AiCallLog` row).
