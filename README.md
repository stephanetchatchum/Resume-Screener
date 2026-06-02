# TalentScreener

A simple Django-based candidate screening app that lets you create job postings, upload resumes (PDF/DOCX), and score candidates using Groq AI.

## Quick overview

- Create and manage job positions
- Upload candidate resumes tied to a job
- Extract text from PDF and DOCX resumes
- Analyze resume content against a job description using Groq AI
- Store an AI-generated summary and fit score for each candidate
- View candidates sorted by score

## Tech stack

- Python 3.14
- Django 6.0.5
- SQLite (`db.sqlite3`) for local development
- Groq AI client (used for scoring)
- `PyPDF2` for PDF extraction
- `python-docx` for DOCX extraction
- `python-dotenv` for local env loading

## Project layout

- `core/` — Django project (`settings.py`, `urls.py`, WSGI/ASGI)
- `screener/` — main app
  - `models.py` — `Job`, `Candidate`
  - `views.py` — job pages, resume upload handlers, AI scoring logic
  - `urls.py` — app routes
  - `templates/screener/` — HTML templates
- `manage.py` — Django management entrypoint

## Setup (Development)

1. Activate the virtual environment:

```powershell
.\myenv\Scripts\Activate.ps1
```

2. Install dependencies. Prefer a `requirements.txt` but you can install directly:

```powershell
python -m pip install Django==6.0.5 PyPDF2==3.0.1 python-docx==1.2.0 python-dotenv==1.2.2 groq==1.2.0
```

3. Environment variables

Create a `.env` file in the project root with values required by the app. At minimum:

```text
GROQ_API_KEY=your_api_key_here
# Add any other secrets or credentials here
```

The project loads `.env` via `python-dotenv` in `screener/views.py`.

4. Database migrations and optional superuser

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. Run the dev server

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Usage

- From the homepage create a new job posting with title and description.
- Open the job detail page and upload a candidate resume (`.pdf` or `.docx`).
- The app extracts the resume text and calls the Groq AI scoring flow to produce a summary and fit score.
- Review candidates on the job page (sorted by score) and click through to view details.

## Development notes

- AI scoring: see `screener/views.py` for the request/response flow to Groq. The model currently referenced in code may be adjusted as models evolve.
- Resume parsing: PDF extraction uses `PyPDF2`, DOCX uses `python-docx`. Add better error handling for malformed files.
- Admin: `screener/admin.py` currently does not register `Job`/`Candidate` by default — consider registering them for quick admin access.
- Tests: add unit tests for parsing and the scoring integration (mock external calls).

## Troubleshooting

- If uploads fail, check `MEDIA_ROOT` and file permission settings.
- If Groq responses error, confirm `GROQ_API_KEY` and network connectivity.

## Next improvements

- Add `requirements.txt` and a `Makefile` or script for common dev tasks
- Register models in `screener/admin.py` and add basic admin views
- Add more robust parsing and fallback strategies for PDFs/DOCX
- Add pagination and search on the job/candidate listings

## Contributing

If you'd like to contribute, open an issue or create a pull request with clear changes and tests where applicable.

---

If you have a partially-written Gmail integration section you'd like preserved, point me to its location and I'll avoid modifying it while updating the rest of the README.
