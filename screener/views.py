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
        model="llama3-8b-8192"
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

def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'screener/job_list.html', {'jobs': jobs})


        