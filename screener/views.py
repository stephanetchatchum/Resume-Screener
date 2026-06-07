from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Job, Candidate
from groq import Groq
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import base64
import json
import PyPDF2
import docx
import io
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq()

#text Extractor
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

#AI analyzer
def analyze_candidate(resume_text, job_description):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an expert HR assistant. Analyze resumes against job descriptions."
            },
            {
                "role": "user",
                "content": f"""Analyze this resume against the job description.
                
                Job Description:
                {job_description}

                Resume:
                {resume_text}

                Provide:
                1. A brief summary of the candidate (3-4 sentences)
                2. A fit score from 0 to 100
                3. Key strengths
                4. Key gaps

                Format your response as:
                SUMMARY: [summary]
                SCORE: [number only]
                STRENGTHS: [strengths]
                GAPS: [gaps]
                """
            }
        ]
    )
    return response.choices[0].message.content

#response parser
def parse_ai_response(response_text):
    lines = response_text.strip().split('\n')
    result = {"summary": "", "score": 0, "strengths": "", "gaps": ""}
    for line in lines:
        if line.startswith("SUMMARY:"):
            result["summary"] = line.replace("SUMMARY:", "").strip()
        elif line.startswith("SCORE:"):
            try:
                result["score"] = float(line.replace("SCORE:", "").strip())
            except:
                result["score"] = 0
        elif line.startswith("STRENGTHS:"):
            result["strengths"] = line.replace("STRENGTHS:", "").strip()
        elif line.startswith("GAPS:"):
            result["gaps"] = line.replace("GAPS:", "").strip()
    return result

#views
def job_list(request):
    query = request.GET.get('q', '')
    if query:
        jobs = Job.objects.filter(title__icontains=query).order_by('-created_at')
    else:
        jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'screener/job_list.html', {'jobs': jobs})

def create_job(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        Job.objects.create(title=title, description=description)
        messages.success(request, 'Job created successfully.')
        return redirect('job_list')
    return render(request, 'screener/create_job.html')

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    query = request.GET.get('q', '')
    if query:
        candidates = job.candidates.filter(name__icontains=query).order_by('-score')
    else:
        candidates = job.candidates.all().order_by('-score')
    return render(request, 'screener/job_detail.html', {'job': job, 'candidates': candidates})

def upload_resume(request, job_id):

    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        resume_file = request.FILES['resume']

        if resume_file.name.endswith('.pdf'):
            resume_text = extract_text_from_pdf(resume_file)
        elif resume_file.name.endswith('.docx'):
            resume_text = extract_text_from_docx(resume_file)
        else:
            messages.error(request, 'Please upload a pdf or DOCX file.')
            return redirect('upload_resume', job_id=job_id)
        
        ai_response = analyze_candidate(resume_text, job.description)
        parsed = parse_ai_response(ai_response)

        Candidate.objects.create(
            job=job,
            name=name,
            email=email,
            resume_text=resume_text,
            summary=parsed['summary'],
            score=parsed['score']
        )
        messages.success(request, f'{name} has been screened and added.')
        return redirect('job_detail', job_id=job_id)
    return render(request, 'screener/upload_resume.html', {'job': job})

def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, f'"{job.title}" has been deleted.')
        return redirect('job_list')
    
    return redirect('job_list')

#Gmail intergratrion

SCOPES = ['HTTPS://www.googleapis.com/auth/gmail.readonly']#asking readonly perms from goodle

CREDENTIALS_FILE = 'credentials.json'

def gmail_auth(request):
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri='http://localhost:8000/oauth2callback/'
    )

    auth_url, state = flow.authorization_url(prompt='consent')

    request.session['state'] = state

    return redirect(auth_url)

def oauth2callback(request):
    state = request.session['state']

    flow = Flow.from_client_config(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri='http://localhost:8000/oauth2callback/'
    )

    flow.fetch_token(authorization_response=request.build_absolute_uri())

    Credentials = flow.credentials

    request.session['gmail_credentials'] = {
        'token': Credentials.token,
        'refresh_token': Credentials.refresh_token,
        'tonken_uri': Credentials.token_uri,
        'client_id': Credentials.client_id,
        'client_secret': Credentials.client_secret,
        'scopes': Credentials.scopes
    }

    return redirect('gmail_scan')

def gmail_scan(request, job_id):
    if 'gmail_credentials' not in request.session:
        return redirect('gmail_auth')
    
    job = get_object_or_404(Job, id=job_id)

    creds = Credentials(**request.session['gmail_credentials'])

    service = build('gmail', 'v1', credentials=creds)

    results = service.user().messages().list(
        userId='me',
        q='has:attachment filename:pdf OR filename:docx',
        maxResults=20
    ).execute()

    messages_list = results.get('messages', [])
    screened = 0

    for msg in messages_list:
        message = service.users().messages().get(
            userId='me', id=msg['id']
        ).execute()

        sender = ''
        for header in messages['payload']['headers']:
            if header['name'] == 'From':
                sender = header['value']

        parts = message['payload'].get('parts', [])

        for part in parts:
            if part['filename'] and (part['filename'].endswith('.pdf') or part['filename'].endswith('.docx')):
                attachment_id = part['body']['attachmentId']

                attachment = service.users().messages().attachments().get(

                ).execute()

                file_data = base64.urlsafe_b64decode(attachment['data'])

                if part['filename'].endswith('.pdf'):
                    resume_text = extract_text_from_pdf(io.BytesIO(file_data))
                else:
                    resume_text = extract_text_from_docx(io.BytesIO(file_data))

                if resume_text:
                    ai_response = analyze_candidate(resume_text, job.description)
                    parsed = parse_ai_response(ai_response)

                    Candidate.objects.create(
                        job=job,
                        name=sender,
                        email=sender,
                        resume_text=resume_text,
                        summary=parsed['summary'],
                        score=parsed['score']
                    )
                    screened += 1

    messages.success(request, f'Scanned Gmail inbox. {screened} candidates screened.')
    return redirect('job_detail', job_id=job_id)
