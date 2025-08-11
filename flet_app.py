import flet as ft
import requests

API_URL = "http://127.0.0.1:5000"

def main(page: ft.Page):
    page.title = "AI Career Coach"
    page.scroll = ft.ScrollMode.ALWAYS
    page.theme_mode = ft.ThemeMode.LIGHT  # Setting light theme

    skills_field = ft.TextField(label="Enter your skills (comma separated)", width=400)
    role_field = ft.TextField(label="Enter your job role (optional)", width=400)
    prediction_result_text = ft.Text()

    def predict_click(e):
        payload = {"skills": skills_field.value, "role": role_field.value}
        try:
            res = requests.post(f"{API_URL}/predict-job", json=payload)
            if res.status_code == 200:
                data = res.json()
                prediction_result_text.value = data.get("message", "Predicted Job Titles:")
                if "predictions" in data:
                    prediction_result_text.value += "\n" + "\n".join(
                        [f"{pred['job_title']} (Confidence: {pred['confidence']:.2f})" for pred in data["predictions"]]
                    )
            else:
                prediction_result_text.value = "Error: " + res.text
        except Exception as ex:
            prediction_result_text.value = "Exception: " + str(ex)
        page.update()

    predict_button = ft.ElevatedButton("Predict Job Titles", on_click=predict_click)

    chatbot_field = ft.TextField(label="Ask your career question", width=400)
    chatbot_result_text = ft.Text()

    def chatbot_click(e):
        payload = {"query": chatbot_field.value}
        try:
            res = requests.post(f"{API_URL}/chatbot", json=payload)
            chatbot_result_text.value = res.json().get("response", "Error fetching response")
        except Exception as ex:
            chatbot_result_text.value = "Exception: " + str(ex)
        page.update()

    chatbot_button = ft.ElevatedButton("Ask Chatbot", on_click=chatbot_click)

    resume_result_text = ft.Text()
    
    def resume_picker_result(e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            try:
                with open(file.path, "rb") as f:
                    file_bytes = f.read()
                res = requests.post(
                    f"{API_URL}/upload-resume",
                    files={"file": (file.name, file_bytes)}
                )
                if res.status_code == 200:
                    data = res.json()
                    extracted_skills = ", ".join(data.get("extracted_skills", []))
                    matched_jobs = "\n".join(
                        [f"Skill: {skill}\n  - " + "\n  - ".join(links) for skill, links in data.get("matched_jobs", {}).items()]
                    )
                    resume_result_text.value = f"Resume Parsing Result:\nExtracted Skills: {extracted_skills}\n\n{matched_jobs if matched_jobs else 'No matched job titles found.'}"
                else:
                    resume_result_text.value = "Error: " + res.text
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
        ft.Text("Job Prediction", size=20, weight=ft.FontWeight.BOLD),
        skills_field,
        role_field,
        predict_button,
        prediction_result_text,
        ft.Divider(),
        ft.Text("Chatbot", size=20, weight=ft.FontWeight.BOLD),
        chatbot_field,
        chatbot_button,
        chatbot_result_text,
        ft.Divider(),
        ft.Text("Resume Parsing", size=20, weight=ft.FontWeight.BOLD),
        upload_resume_button,
        resume_result_text,
    ], spacing=20, scroll=ft.ScrollMode.ALWAYS, alignment=ft.MainAxisAlignment.CENTER)

    page.add(main_column)

ft.app(target=main)