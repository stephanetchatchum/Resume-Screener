# Resume Screener

A simple Django-based candidate screening app that lets you create job postings, upload resumes in PDF or DOCX format, and score candidates automatically using Groq AI.

## Features

- Create and manage job positions
- Upload candidate resumes for a specific job
- Extract text from PDF and DOCX resumes
- Analyze resume content against the job description using Groq AI
- Store candidate summary and fit score
- View candidates sorted by score

## Tech Stack

- Python 3.14
- Django 6.0.5
- SQLite (`db.sqlite3`)
- Groq AI client
- PyPDF2 for PDF text extraction
- python-docx for DOCX text extraction
- python-dotenv for environment variable loading

## Project Structure

- `core/` - Django project settings and URL configuration
- `screener/` - main application
  - `models.py` - `Job` and `Candidate` models
  - `views.py` - job pages, resume upload, AI scoring logic
  - `urls.py` - app routes
  - `templates/screener/` - HTML templates for UI
- `manage.py` - Django management wrapper
- `db.sqlite3` - local SQLite database file

## Setup

1. Activate the virtual environment:

   ```powershell
   .\myenv\Scripts\Activate.ps1
   ```

2. Install required packages:

   ```powershell
   python -m pip install Django==6.0.5 PyPDF2==3.0.1 python-docx==1.2.0 python-dotenv==1.2.2 groq==1.2.0
   ```

3. Prepare environment variables for Groq AI.

   Create a `.env` file in the project root if you want to store secrets locally:

   ```text
   GROQ_API_KEY=your_api_key_here
   ```

   The app loads environment variables using `dotenv.load_dotenv()` in `screener/views.py`.

4. Run migrations:

   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Start the development server:

   ```powershell
   python manage.py runserver
   ```

6. Open the app in your browser:

   ```text
   http://127.0.0.1:8000/
   ```

## Usage

- Visit the homepage to see the list of jobs.
- Create a new job posting with a title and description.
- Open a job detail page and upload a candidate resume.
- The app extracts resume text, sends it to Groq AI for analysis, and saves a summary and fit score.
- Candidate listings show the score and the AI-generated summary.

## Notes

- `screener/views.py` currently uses the Groq model `llama-3.3-70b-versatile`.
- The app supports `.pdf` and `.docx` uploads only.
- `DEBUG` is enabled in `core/settings.py`, so this setup is for development only.
- `screener/admin.py` is not registering models yet, so Django admin is not configured by default.

## Optional Improvements

- Add `requirements.txt` for reproducible installs
- Register `Job` and `Candidate` in `screener/admin.py`
- Add candidate detail views and display strengths/gaps
- Add stronger error handling for resume parsing and AI responses
