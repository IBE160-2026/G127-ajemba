# Gruppe G127

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

Repoet inneholder gruppens applikasjon og dokumentasjon av utvikling, testing og kvalitetssikring med KI.

## Medlemmer

- Augustina Obiageli Ajemba

## Install and start

Windows commands first (PowerShell). You need Python 3.12 or 3.13.

1. Check your Python version. It must print 3.12.x or 3.13.x:

   ```powershell
   python --version
   ```

2. Create a virtual environment in the project folder and activate it:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell says "running scripts is disabled on this system", run this first. It only applies to the current terminal window:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

   Or use Command Prompt (cmd) instead and activate with:

   ```bat
   .venv\Scripts\activate.bat
   ```

3. Install the requirements (exact versions):

   ```powershell
   pip install -r requirements.txt
   ```

4. Start the app. No `.env` file is needed. It runs `migrate`, marks stuck lectures as failed, and starts the web app and the background worker together:

   ```powershell
   python run.py
   ```

   Open http://localhost:8000/ in your browser. Press Ctrl+C to stop; it stops the web app and the worker. If port 8000 is busy, use `python run.py --port 8001`.

5. Run the tests (also without a `.env`):

   ```powershell
   python manage.py test
   ```

On macOS or Linux the same steps work with `python3 -m venv .venv` and `source .venv/bin/activate`.

To change settings, copy `.env.example` to `.env`. The `.env` file and `db.sqlite3` are never committed. The SQLite file is the only copy of your data.

## Accounts

Story 1.2. Start the app (`python run.py`) and open http://localhost:8000/.

- **Register:** click "Register" (http://localhost:8000/accounts/register/), type an email and a password and press "Register". The password must pass Django's checks (not too short, not too common, not only digits). You are logged in and land on "My lectures". The same email in another letter case (`Amara@Example.com`) counts as the same account.
- **Log in:** click "Log in" (http://localhost:8000/accounts/login/). After 5 wrong passwords in 15 minutes for the same email from the same computer, further tries are refused, even with the right password. Wait 15 minutes and try again.
- **Log out:** click "Log out" at the top. It sends a POST request, so opening the logout address by typing it does nothing. Logging out also clears the essay draft backup kept in your browser (`localStorage` keys starting with `recall:`).
- **Not in v1:** there is no email check and no password reset. Please remember your password.

Passwords are stored as hashes, never as text. The login-failure counters are kept in the `recall_cache` database table, made by `python manage.py createcachetable` (`python run.py` runs it for you). htmx is kept in `static/vendor/` (source and hash in `htmx.SOURCE.txt`) and is never loaded from the internet. Static files are served only while `RECALL_ENV` is `local` (the default); with another value the pages load without styling and htmx until a static file server is added.

## Privacy rules

Story 1.3. Each user sees only their own lectures.

- **Own lectures only:** every page gets a lecture through `Lecture.objects.for_user(user)` (or the helpers in `lectures/services.py`), never by a bare id. Another user's lecture, a lecture id that does not exist, and a write to an example lecture all give the same "Page not found" (404) page, so nobody can tell whether an id belongs to someone else. A logged-out visitor is sent to the login page and sees nothing.
- **One public exception, added later:** the Example Lecture (Demo Mode) is the only lecture anyone can open without owning it. It is built in epic-demo-readme and cannot be edited or deleted.
- **Two guard tests protect every later epic.** Run them with `python manage.py test`:
  - `config/test_url_access.py` reads the address list in `urls.py`, asks for every address as a second user (using the first user's lecture id) and as a logged-out visitor, and fails if any lecture data appears. A new address is covered automatically. A new page that logged-out visitors may open must be added on purpose to `PUBLIC_URL_NAMES` in that file.
  - `core/tests.py` reads the imports of every module and fails if anything but `core/ai_client.py` imports the Gemini library, anything but `core/pdf_text.py` imports pypdf, anything in the app imports pdfplumber (the `evaluation/` folder is exempt), anything but `core/jobs.py` imports django-q2, or a pure module (scoring, matching, ...) imports models, requests or network code. It also checks itself against a deliberately broken example module.

The upload page is at `/lectures/upload/`. To try the rules by hand without it, make two accounts and add a lecture to the first one from the Django shell (`python manage.py shell`):

```python
from accounts.models import User
from lectures.models import Lecture
Lecture.objects.create(user=User.objects.get(email="first@example.com"), title="My secret lecture")
```

## What we checked and what we did not

Story 2.1 (FR-4). We checked how well the text can be read from a real PowerPoint-exported PDF (test lecture 1, 12 slides on hand hygiene, my own work with ChatGPT help, see `evaluation/testset/test-lecture-1-NOTE.md`).

- **Result:** pypdf and pdfplumber both gave 0 broken words (hyphenated line breaks, run-together words, ligature glyphs) in the 5-slide sample. The average is about 338 characters per page, so the limit of 100 characters per page still looks right for this deck. pdfplumber mixed the columns of multi-column slides, which can change the meaning, so the app uses **pypdf 7.1.1**. Details and the sample: [docs/extraction-test.md](docs/extraction-test.md).
- **Not checked yet:** image-heavy decks (only one text-rich deck was tested; a second, freely licensed deck comes later), and whether the page header and footer text should be removed.

**PDF requirements:** text-based PDF only. A PDF exported from PowerPoint works; a scanned or photographed one has no readable text. See Upload limits below.

## Upload limits

Log in and open **Upload** (`/lectures/upload/`) to add one PDF.

- **10 MB** at most. Reading stops at 10 MB plus one byte.
- **50 pages** at most.
- **Scanned or image-only PDFs are rejected.** So are encrypted and corrupt PDFs, and PDFs with fewer than 100 characters of text per page on average. The message says the file has no text we can read.
- Text is read in a separate process that is stopped after 20 seconds.
- The PDF is **not kept**. Only the text of each page is stored, and every temporary copy is deleted, also when the file is rejected. A rejected file creates no lecture.

## AI notice and daily limit

**AI notice.** Before the first upload, the upload page shows this notice and the user must tick "I have read this notice about Google's terms." The server refuses any upload without a current acknowledgement. If the notice changes, `NOTICE_VERSION` goes up and everyone must tick again.

> Recall sends your slides and your essay answers to Google's Gemini API. This is what Google's terms say.
>
> **Unpaid quota** ("Unpaid Services"):
> - Free tier: "Content used to improve our products"
> - "To help with quality and improve our products, human reviewers may read, annotate, and process your API input and output."
> - "Do not submit sensitive, confidential, or personal information to the Unpaid Services."
>
> **If you are in the EEA, Switzerland or the UK:**
> - "If you're in the European Economic Area, Switzerland, or the United Kingdom, the terms under "How Google uses Your Data" in "Paid Services" apply to all Services, including Google AI Studio and unpaid quota in the Gemini API, even though they are offered free of charge."
> - Paid Services: "Google doesn't use your prompts (including associated system instructions, cached content, and files such as images, videos, or documents) or responses to improve our products"
>
> Read the terms: [Gemini API Additional Terms of Service](https://ai.google.dev/gemini-api/terms). Only upload files you are allowed to share.

Source: <https://ai.google.dev/gemini-api/terms>, checked on 2026-10-17 (the terms page showed "Effective March 23, 2026" and "Last updated 2026-04-28 UTC"). The quotes are stored in `_bmad-output/initiative-recall/architecture-recall/gemini-terms-checked-2026-10-17.md`. The notice shows the quotes about data use that matter to a student; the stored file also holds quotes for the developer, for example "Use Restrictions". In v1 the free Gemini key is used only by the builder, locally.

**Daily limit.** Each user can upload **5 PDFs per day**. Only accepted uploads count: a file rejected for size, type, pages or missing text is not counted, and neither is an upload refused for the notice or the limit. Deleting a lecture does not give an upload back.

- `UPLOADS_PER_DAY` (default `5`) sets the limit.
- `LIMIT_TIME_ZONE` (default `Europe/Oslo`) decides when a day starts: at midnight in that time zone, also across summer and winter time.
- Both are set in `.env` (see `.env.example`). A value below 1 or an unknown time zone name stops the app at start.

## How processing works

After an upload, the lecture is saved with the status **Processing** and a background job is queued. `python run.py` starts the web app and the worker (django-q2, one worker) together, and Ctrl+C stops both. If one of the two stops by itself, `run.py` stops the other.

- **You can close the page.** The worker keeps going. My lectures (`/lectures/`) shows **Processing…**, **Ready** or **Failed** and updates itself every 3 seconds. The Processing page (`/lectures/<id>/`) shows two steps, "Reading your PDF" (done) and "Writing the summary" (in progress), and no percentage or timer. It stops asking at Ready or Failed.
- **Only an id goes in the queue.** Never slide text. A job changes the status with one conditional update, so the same lecture queued twice runs once.
- **Stuck lectures.** A lecture that stays in Processing for more than 10 minutes (`STALE_MINUTES`) is shown as Failed. This is checked when `run.py` starts and whenever a status is read.
- **Try again.** A failed lecture has a **Try again** button, at most 3 times per lecture. A retry does not count as a new upload.
- **AI budget.** `AI_CALLS_PER_USER_PER_DAY` (default 30) and `AI_CALLS_GLOBAL_PER_DAY` (default 200) are counted from the AI call log. When either is used up, no job is queued and the user sees a message. Nothing writes to that log yet.
- **What does not exist yet:** the summary itself. For now the job only ends the lecture as **Failed**, so every upload ends as Failed. The app does not call any AI and needs no Gemini key.
- **Known limit:** on macOS and Linux, stopping `run.py` with `kill` or SIGTERM may leave the web app and the worker running. Ctrl+C is the supported way to stop it. On Windows, `run.py` also stops both if it is killed.
- **Known limit:** when you press Ctrl+C, django-q2 may print CRITICAL lines such as "reincarnated worker ... after sudden death" before it stops. The terminal sends Ctrl+C to the worker's own child processes too, and the worker restarts them for a moment. The result is correct: `run.py` stops, and the web app and the worker are gone. It only looks alarming.
- **Windows:** django-q2 was tested on Windows 11 with Python 3.13. Result: [docs/django-q2-windows-test.md](docs/django-q2-windows-test.md).

## If you deploy this

Recall is built to run locally in v1. Before it runs anywhere else:

- Turn debug off (`RECALL_ENV` other than `local`) and set a real `SECRET_KEY`.
- Set `ALLOWED_HOSTS` to your host name and use HTTPS.
- Use a production server that runs on the host, for example Waitress on Windows, not `runserver`.
- Run exactly one worker. The queue and the status changes are built for one.
- Use a paid Gemini key. In v1 the free key is used only by the builder, locally; offering Recall to users in the EEA, Switzerland or the UK needs a paid key under Google's terms.
- Do a privacy review. The slide text of every lecture is stored and sent to Google.
- The SQLite file (`db.sqlite3`) is the only copy of the data. There are no backups.
