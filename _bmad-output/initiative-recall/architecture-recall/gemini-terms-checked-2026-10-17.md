# Gemini API terms: what was checked

Checked on **2026-10-17** by fetching the pages below. The terms page shows "Effective March 23, 2026" and "Last updated 2026-04-28 UTC". Quotes are verbatim. Re-check before every release; if the text changes, change the notice and raise `notice_version` (AD-16).

## Source 1: https://ai.google.dev/gemini-api/terms

Section "Unpaid Services", subsection "How Google Uses Your Data":

- "When you use Unpaid Services, including, for example, Google AI Studio and the unpaid quota on Gemini API, Google uses the content you submit to the Services and any generated responses to provide, improve, and develop" (the fetched text ends here)
- "To help with quality and improve our products, human reviewers may read, annotate, and process your API input and output."
- "This includes disconnecting this data from your Google Account, API key, and Cloud project before reviewers see or annotate it."
- "Do not submit sensitive, confidential, or personal information to the Unpaid Services."

Section "Unpaid Services", body text before that subsection (EEA, Switzerland, UK):

- "If you're in the European Economic Area, Switzerland, or the United Kingdom, the terms under "How Google uses Your Data" in "Paid Services" apply to all Services, including Google AI Studio and unpaid quota in the Gemini API, even though they are offered free of charge."

Section "Paid Services", subsection "How Google Uses Your Data":

- "When you use Paid Services, including, for example, the paid quota of the Gemini API, Google doesn't use your prompts (including associated system instructions, cached content, and files such as images, videos, or documents) or responses to improve our products"
- "For Paid Services, Google logs prompts and responses for a limited period of time, solely for detecting and preventing violations of the Prohibited Use Policy"

Section "Use Restrictions":

- "You may use only Paid Services when making API Clients available to users in the European Economic Area, Switzerland, or the United Kingdom."

## Source 2: https://ai.google.dev/pricing

- Tier cards: Free "Content used to improve our products"; Paid "Content **not** used to improve our products".
- Row "Used to improve our products" for Gemini 3.8 Flash and 3.6 Flash: Free Tier "Yes", Paid Tier "No". The row varies by model; some models are not offered on the free tier.

## Notes

- The terms address "you", the API customer who owns the key. They do not say whose location counts when someone else's text is sent through that key. The notice therefore repeats the terms and does not decide this.
- The "Use Restrictions" sentence is about making an API client available to users in these regions. See AD-16 and the memlog for how this project handles it.
- Pricing page text was cut off at about 39,000 of 84,000 characters; the rows above come from the part that was read.
