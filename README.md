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
