# 03 Upload

Reached from: top bar, My lectures. Leads to: Processing (04).

## Wide screen

```
+--------------------------------------------------------------------------+
| Recall   My lectures   Upload      Text size: [A] [A+] [A++]   Log out    |
+--------------------------------------------------------------------------+
|  Upload a lecture                                                        |
|                                                                          |
|  +--------------------------------------------------------------------+  |
|  | (i) Recall sends your slides and your essay answers to Google's    |  |
|  |     Gemini API. This is what Google's terms say:                   |  |
|  |     "...human reviewers may read, annotate, and process your API   |  |
|  |     input and output."  (more quotes: unpaid quota, EEA/CH/UK,    |  |
|  |     paid services; full text in EXPERIENCE.md, Upload notice)      |  |
|  |     Read the terms (link).                                         |  |
|  |     Only upload files you are allowed to share.                    |  |
|  |     [ ] I have read this notice about Google's terms.              |  |
|  +--------------------------------------------------------------------+  |
|                                                                          |
|  Choose a PDF file                                                       |
|  [ 📄 Choose file ]   No file chosen                                     |
|                                                                          |
|  Rules                                                                   |
|   • PDF with text (not a scan)                                           |
|   • Up to 50 pages                                                       |
|   • Up to 10 MB                                                          |
|   • You can upload 5 lectures per day. Uploads left today: 4             |
|                                                                          |
|  [ ⬆ Upload and make summary ]                                           |
|  Choose a file and tick the notice first.   <- shown while disabled  |
+--------------------------------------------------------------------------+
```

## Error example

```
|  Choose a PDF file                                                       |
|  [ 📄 Choose file ]   slides-scan.pdf                                    |
|  (!) This file has no text we can read. Choose a PDF with text,          |
|      not a scan.                                                         |
```

Other messages:
- "This PDF has more than 50 pages. Choose a shorter file."
- "This file is larger than 10 MB. Choose a smaller file."
- "Choose a PDF file."
- "You have used your 5 uploads for today. You can upload again tomorrow."

## Demo Mode

A demo banner is on top. The upload button area shows: "Processing needs an API key. See the README."

## Notes
- The AI notice is shown before the first upload (FR-6). After the tick, it shows as a short line.
- A rejected file creates no lecture and does not count as an upload (FR-7).
- Phone: one column, full-width buttons.
