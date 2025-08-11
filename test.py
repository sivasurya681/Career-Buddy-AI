import flet as ft
import joblib
import prediction
import resume_parser
import chatbot
import pandas as pd
import re
import os

# Load dataset for job link retrieval and ensure column names are lowercase.
print("Loading dataset for UI...")

if not os.path.exists("dataset_clean.csv"):
    print("Error: dataset_clean.csv not found!")
    df = None
else:
    df = pd.read_csv("dataset_clean.csv")
    df.columns = df.columns.str.lower()
    print("Dataset loaded.")

def get_job_links(job_title):
    return [f"https://jobs.example.com/{job_title.replace(' ', '-')}/apply" for _ in range(5)]

def main(page: ft.Page):
    page.title = "AI Career Coach"
    page.scroll = ft.ScrollMode.ALWAYS

    skills_field = ft.TextField(label="Enter your skills (comma separated)", width=300)
    role_field = ft.TextField(label="Enter your job role (optional)", width=300)
    prediction_result_text = ft.Text()

    def predict_click(e):
        skills = skills_field.value
        role = role_field.value
        if not skills:
            prediction_result_text.value = "Error: Skills are mandatory"
            page.update()
            return
        
        input_text = (role + " " if role else "") + skills
        preds = prediction.predict_job_titles(input_text)
        
        if not preds or preds[0][1] < 0.2:
            prediction_result_text.value = "Upgrade your skill"
        else:
            results = []
            for title, prob in preds:
                title_lower = title.lower()
                if df is not None:
                    matching = df[df["job title"].str.contains(re.escape(title_lower))]
                    companies = matching["company"].drop_duplicates().tolist()
                else:
                    companies = ["Data not available"]
                
                results.append({
                    "job_title": title,
                    "confidence": prob,
                    "companies": companies[:10]
                })
            
            prediction_result_text.value = "Predicted Job Titles:"
            for pred in results:
                prediction_result_text.value += f"\n{pred['job_title']} (Confidence: {pred['confidence']:.2f})"
        
        page.update()

    predict_button = ft.ElevatedButton("Predict Job Titles", on_click=predict_click)

    chatbot_field = ft.TextField(label="Ask your career question", width=300)
    chatbot_result_text = ft.Text()

    def chatbot_click(e):
        query = chatbot_field.value
        if not query:
            chatbot_result_text.value = "Error: Please enter a query"
        else:
            response = chatbot.get_chatbot_response(query)  # FIXED
            chatbot_result_text.value = response if response else "Error fetching response"
        page.update()

    chatbot_button = ft.ElevatedButton("Ask Chatbot", on_click=chatbot_click)

    resume_result_text = ft.Text()
    
    def resume_picker_result(e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            try:
                file_path = file.path
                resume_info = resume_parser.parse_resume(file_path)  # FIXED
                
                text = "Resume Parsing Result:\nExtracted Skills:\n"
                text += ", ".join(resume_info.get("extracted_skills", [])) + "\n\n"
                matched = resume_info.get("matched_jobs", {})
                
                if matched:
                    for skill, matches in matched.items():
                        text += f"Skill: {skill}\n"
                        for link in matches:
                            text += f"  - {link}\n"
                else:
                    text += "No matched job titles found."
                
                resume_result_text.value = text
            except Exception as err:
                resume_result_text.value = "Error reading file: " + str(err)
        else:
            resume_result_text.value = "No file selected."
        page.update()

    file_picker = ft.FilePicker(on_result=resume_picker_result)
    page.overlay.append(file_picker)
    
    def upload_resume_click(e):
        file_picker.pick_files()
    
    upload_resume_button = ft.ElevatedButton("Upload Resume", on_click=upload_resume_click)

    main_column = ft.Column([
        ft.Text("Job Prediction", size=20),
        skills_field,
        role_field,
        predict_button,
        prediction_result_text,
        ft.Divider(),
        ft.Text("Chatbot", size=20),
        chatbot_field,
        chatbot_button,
        chatbot_result_text,
        ft.Divider(),
        ft.Text("Resume Parsing", size=20),
        upload_resume_button,
        resume_result_text,
    ], spacing=20, scroll=ft.ScrollMode.ALWAYS)

    page.add(main_column)

ft.app(target=main)