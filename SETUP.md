# Medical Diagnosis System — Setup & Run Guide

This guide explains how to clone, install, and run the Medical Diagnosis System locally on Windows (also works on macOS/Linux with minor adjustments).

Prerequisites
- Python 3.10+ installed and on PATH.
- Git (to clone from GitHub) or download the ZIP from the repo.
- (Optional) A Supabase project and keys if you want persistent storage.
- (Optional) Google Generative AI credentials if you want AI features (see "Generative AI notes").

1. Clone the repository

```powershell
git clone <REPO_URL>
cd test-medai-main
```

2. Create and activate a virtual environment (recommended)

```powershell
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# or legacy cmd
.\.venv\Scripts\activate
```

3. Install Python dependencies

The project includes a `requirements.txt`. Install packages with:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

If `pip install` fails for a specific package, read the error and install system dependencies as instructed.

4. Configure environment variables (optional but recommended)

Create a `.env` file at the project root to configure optional services such as Supabase and Google API:

```
SUPABASE_URL=https://your-supabase-url
SUPABASE_KEY=your-supabase-key
GOOGLE_API_KEY=your-google-api-key
```

Notes:
- If you don't provide Supabase credentials the app will run with fallback behavior (no persistent DB).
- If you don't provide a valid `GOOGLE_API_KEY` or do not want AI features, the server will continue but AI features may be unavailable.

5. Start the API server

Run the FastAPI server (recommended in a separate terminal so you can see logs):

```powershell
python api_server.py
```

You should see logs similar to:
- "Starting server on http://localhost:8000"
- Diagnostic messages about Supabase / Generative AI availability.

6. Serve the frontend over HTTP (do NOT open index.html with file://)

A `file://` origin often blocks fetch/XHR requests and causes JavaScript errors. From the project folder:

```powershell
python -m http.server 8001
```

Open the UI at:

http://localhost:8001/index.html

7. Common API tests (PowerShell)

PowerShell's `curl` is an alias for `Invoke-WebRequest`. Use `Invoke-RestMethod` or `curl.exe` instead:

```powershell
# Register (replace with your email)
Invoke-RestMethod -Uri http://localhost:8000/api/auth/register -Method POST -Headers @{ 'Content-Type' = 'application/json' } -Body '{"email":"tester@example.com","name":"Tester","phone":"12345"}'

# Login
Invoke-RestMethod -Uri http://localhost:8000/api/auth/login -Method POST -Headers @{ 'Content-Type' = 'application/json' } -Body '{"email":"tester@example.com"}'

# Or use curl.exe if available
curl.exe -v -H "Content-Type: application/json" -X POST http://localhost:8000/api/auth/login -d '{"email":"tester@example.com"}'
```

8. Browser troubleshooting (DevTools)

- Open DevTools (F12) → Console: check for JavaScript errors.
- Network tab: inspect requests to `http://localhost:8000/api/...` and view response status and body.
- Common issue: `Uncaught SyntaxError: Identifier 'API_BASE_URL' has already been declared` — this is caused by duplicate `const API_BASE_URL` declarations. The project expects `API_BASE_URL` to be defined in `script.js`. If you see this error, remove the duplicate declaration from `index.html`.

9. Generative AI notes (Gemini / Google GenAI)

- The code may attempt to initialize Google's generative client (Gemini) using legacy bindings (`google.generativeai`). The repo includes a more robust init that tries several candidate model names and lists available models if supported.
- If you don't want AI features or your API key is not ready, you can:
  - Leave `GOOGLE_API_KEY` unset (the server will continue to run but AI features will be disabled), or
  - Edit `main.py` to skip or comment out the generative AI initialization block.

To fully enable AI features, install the supported client (follow Google's docs) and provide a valid key in `.env`.

10. Logs and debugging

- Application logs: `.cursor/debug.log` (project root) — useful for internal debug entries.
- Server console: shows startup messages and errors from FastAPI/uvicorn.
- If authentication fails from the UI, copy server logs and the Network response body from DevTools.

11. Optional: add a favicon (optional)

If you see a 404 for `favicon.ico`, either ignore it or add an icon file at the project root and update `index.html`:

```html
<link rel="icon" href="favicon.ico">
```

12. Helpful tips

- Always serve the frontend via HTTP (python -m http.server) during development.
- If PowerShell `curl` behaves unexpectedly, use `curl.exe` or `Invoke-RestMethod`.
- Restart the server after editing `main.py` to see changes.




