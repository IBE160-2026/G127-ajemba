"""The upload notice (FR-6, AD-16). One source for the page, the README text and the tests.

The wording is EXPERIENCE.md "Upload notice (exact text)". The quotes are Google's own words and
must not be reworded. The stored source is
_bmad-output/initiative-recall/architecture-recall/gemini-terms-checked-2026-10-17.md.
When Google's text changes: change the quotes here and raise NOTICE_VERSION, so every user
must read the notice again.
"""

NOTICE_VERSION = 1
TERMS_URL = "https://ai.google.dev/gemini-api/terms"
TERMS_LINK_TEXT = "Gemini API Additional Terms of Service"
CHECKED_ON = "2026-10-17"

INTRO = "Recall sends your slides and your essay answers to Google's Gemini API. This is what Google's terms say."
OUTRO = "Only upload files you are allowed to share."
CHECKBOX_LABEL = "I have read this notice about Google's terms."
SHORT_LINE = "You have read the notice about Google's terms."

UNPAID_HEADING_BOLD = "Unpaid quota"  # only these words are bold in EXPERIENCE.md
UNPAID_HEADING_REST = ' ("Unpaid Services"):'
EEA_HEADING = "If you are in the EEA, Switzerland or the UK:"

# Each item is (text before the quote, the quote exactly as Google wrote it).
UNPAID_ITEMS = [
    ("Free tier: ", "Content used to improve our products"),
    ("", "To help with quality and improve our products, human reviewers may read, annotate, and process your API input and output."),
    ("", "Do not submit sensitive, confidential, or personal information to the Unpaid Services."),
]
EEA_ITEMS = [
    ("", "If you're in the European Economic Area, Switzerland, or the United Kingdom, the terms under \"How Google uses Your Data\" in \"Paid Services\" apply to all Services, including Google AI Studio and unpaid quota in the Gemini API, even though they are offered free of charge."),
    ("Paid Services: ", "Google doesn't use your prompts (including associated system instructions, cached content, and files such as images, videos, or documents) or responses to improve our products"),
]

QUOTES = [quote for _, quote in UNPAID_ITEMS + EEA_ITEMS]
