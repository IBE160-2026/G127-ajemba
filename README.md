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

4. Start the app. No `.env` file is needed. It runs `migrate` and starts the web app:

   ```powershell
   python run.py
   ```

   Open http://localhost:8000/ in your browser. Press Ctrl+C to stop; it stops the web app too. If port 8000 is busy, use `python run.py --port 8001`.

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
