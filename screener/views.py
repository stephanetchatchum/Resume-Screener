from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Job, Candidate
from groq import Groq
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
        model="llama3-8b-8192",
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
            result["summary"] = line.replace("SUMMARY:" "").strip()
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