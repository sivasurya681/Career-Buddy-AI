import requests
import os
from flet import Markdown

GEMINI_API_KEY = "AIzaSyCvMakRfm6bcYebvZ1MHIcqX5soVb9RpTY"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"

ALLOWED_TOPICS = {
    "career", "job", "role", "certificate", "certification", "resume", "cv",
    "interview", "salary", "skills", "learning", "learn", "language", "coding", "code", "courses", "education", "hiring",
    "recruitment", "linkedin", "udemy", "coursera", "promotion", "offer letter",
    "internship", "training", "professional growth", "remote job", "on-site job",
    "work-life balance", "career advice", "networking", "job portal", "freelancing",
    "project management", "personal branding", "career switch", "mock interview",
    "job fair", "career goals", "career planning", "career growth", "self improvement",
    "technical skills", "soft skills", "leadership", "team management", "communication skills",
    "negotiation skills", "online courses", "job search", "employee benefits",
    "job responsibilities", "career mentoring", "industry trends", "job descriptions",
    "performance review", "appraisal", "job openings", "career change", "headhunting",
    "job satisfaction", "career counseling", "employment opportunities", "career achievements",
    "job vacancies", "career objectives", "cover letter", "professional resume",
    "career advancement", "industry certification", "career seminars", "career workshops",
    "career webinars", "career conferences", "resume writing", "career breaks",
    "career tips", "career coaching", "skill enhancement", "portfolio building",
    "professional branding", "job relocation", "career transition", "online learning",
    "career consultation", "company culture", "personal development", "employer expectations",
    "career exposure", "salary negotiation", "career evaluation", "career challenges",
    "industry networking", "career pathways", "career flexibility", "career roadmap",
    "career decisions", "career resources", "career forums", "career blogs",
    "career opportunities", "career fairs", "career partnerships", "career references",
    "career highlights", "job offers"
}

def is_valid_query(user_input):
    user_input_lower = user_input.lower()
    return any(topic in user_input_lower for topic in ALLOWED_TOPICS)

def get_gemini_response(prompt):
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(GEMINI_ENDPOINT, headers=headers, params=params, json=payload)
        response.raise_for_status()
        data = response.json()
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "I'm sorry, but I couldn't generate a response at the moment."
    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"
    except (ValueError, KeyError, IndexError) as e:
        return f"Error parsing response: {e}"

def get_chatbot_response(query):
    if not is_valid_query(query):
        return [Markdown("I'm only able to answer career-related questions.")]

    answer = get_gemini_response(query)
    lines = answer.split('\n')
    widgets = []
    for line in lines:
        line = line.strip()
        if line.startswith("- ") or line.startswith("•"):
            widgets.append(Markdown(f"• {line[2:].strip()}"))
        elif line.strip():
            if line.endswith(":"):
                widgets.append(Markdown(f"## {line}"))  # Use Markdown syntax for headers
            else:
                widgets.append(Markdown(line))
    return widgets

if __name__ == "__main__":
    print("Career Chatbot (Type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Exiting Chatbot. Goodbye!")
            break
        responses = get_chatbot_response(user_input)
        for r in responses:
            print("•", r.value)