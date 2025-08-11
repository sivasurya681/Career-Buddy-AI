import os
import requests
import PyPDF2
from bs4 import BeautifulSoup

# API Key and Endpoint for Gemini
GEMINI_API_KEY = "AIzaSyCvMakRfm6bcYebvZ1MHIcqX5soVb9RpTY"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

# Function to extract skills using Gemini API
def extract_skills_with_gemini(resume_text):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""
                        Extract only skills from this resume text:

                        {resume_text}

                        Return a clean list, separated by commas (e.g., Python, Java, Teamwork).
                        """
                    }
                ]
            }
        ]
    }

    response = requests.post(GEMINI_ENDPOINT, headers=headers, json=data)

    if response.status_code == 200:
        response_json = response.json()
        return response_json["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"Error: {response.status_code}, {response.text}"

# Function to fetch a single best-matching job link from LinkedIn
def get_best_linkedin_job(skill):
    headers = {"User-Agent": "Mozilla/5.0"}
    linkedin_url = f"https://www.linkedin.com/jobs/search?keywords={skill.replace(' ', '%20')}"
    
    response = requests.get(linkedin_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        job_listing = soup.find("a", class_="base-card__full-link", href=True)
        if job_listing:
            return job_listing["href"]
    return "No matching job found."

# Main function for resume parsing
def parse_resume(pdf_path):
    if not os.path.exists(pdf_path):
        return {"error": "File not found"}

    resume_text = extract_text_from_pdf(pdf_path)
    extracted_skills = extract_skills_with_gemini(resume_text)

    matched_jobs = {}
    for skill in extracted_skills.split(","):
        job_link = get_best_linkedin_job(skill.strip())
        matched_jobs[skill.strip()] = job_link

    return {"extracted_skills": extracted_skills, "matched_jobs": matched_jobs}

if __name__ == "__main__":
    sample_pdf = "F:\\Vaalka nadagama\\sample_resume.pdf"  # Replace with an actual file path
    print(parse_resume(sample_pdf))
