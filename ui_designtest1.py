import flet as ft
import prediction
import resume_parser
import chatbot
import pandas as pd
import os
import webbrowser

print("Loading dataset for UI...")

if not os.path.exists("dataset_clean.csv"):
    print("Error: dataset_clean.csv not found!")
    df = None
else:
    df = pd.read_csv("dataset_clean.csv")
    df.columns = df.columns.str.lower()
    print("Dataset loaded successfully.")

def main(page: ft.Page):
    page.title = "AI Career Coach"
    page.scroll = ft.ScrollMode.ALWAYS
    page.theme_mode = "light"

    # Function to handle tab switching
    def show_tab(index):
        for i, content in enumerate(tab_contents):
            content.visible = i == index
        page.update()

    # ============================ Resume Analysis Tab ============================
    resume_result_column = ft.Column()
    resume_loading = ft.Text(visible=False)

    def resume_picker_result(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            resume_loading.value = "Parsing resume..."
            resume_loading.visible = True
            resume_result_column.controls.clear()
            page.update()

            # Parse the resume
            resume_info = resume_parser.parse_resume(file_path)

            resume_loading.visible = False  # Hide loading text
            extracted_skills = resume_info.get("extracted_skills", [])
            matched_jobs = resume_info.get("matched_jobs", {})

            if not extracted_skills:
                resume_result_column.controls.append(ft.Text("No skills found."))
            else:
                resume_result_column.controls.append(
                    ft.Text(f"Extracted Skills: {', '.join(extracted_skills)}", size=16, weight=ft.FontWeight.BOLD)
                )

                for skill, matches in matched_jobs.items():
                    if matches:
                        job_link = matches[0]  # Take only the first job link per skill
                        skill_text = ft.Text(f"Skill: {skill}", size=14, weight=ft.FontWeight.BOLD)
                        job_button = ft.ElevatedButton(
                            text=f"Find {skill} Jobs",
                            on_click=lambda e, link=job_link: webbrowser.open(link)
                        )
                        resume_result_column.controls.append(ft.Column([skill_text, job_button], spacing=5))

            page.update()
        else:
            resume_result_column.controls.append(ft.Text("No file selected."))
            page.update()

    file_picker = ft.FilePicker(on_result=resume_picker_result)
    page.overlay.append(file_picker)
    upload_resume_button = ft.ElevatedButton("Upload Resume", on_click=lambda e: file_picker.pick_files())

    resume_tab = ft.Column([
        ft.Container(ft.Text("Resume Analysis", size=20), alignment=ft.alignment.center),
        ft.Container(ft.Row([upload_resume_button], alignment=ft.MainAxisAlignment.CENTER)),
        resume_loading,
        resume_result_column
    ], spacing=15, visible=True)

    # ============================ Job Recommendation Tab ============================
    job_recommendation_column = ft.Column()
    
    def recommend_jobs(e):
        skill_input_value = skill_input.value.strip().lower()
        job_role_input_value = job_role_input.value.strip().lower()

        if not skill_input_value:
            job_recommendation_column.controls.clear()
            job_recommendation_column.controls.append(ft.Text("Please enter a skill."))
            page.update()
            return

        job_recommendations = prediction.predict_job(skill_input_value, job_role_input_value)

        job_recommendation_column.controls.clear()
        if job_recommendations:
            job_recommendation_column.controls.append(ft.Text("Recommended Jobs:", size=16, weight=ft.FontWeight.BOLD))
            
            for job, link in job_recommendations.items():
                job_button = ft.ElevatedButton(text=job, on_click=lambda e, url=link: webbrowser.open(url))
                job_recommendation_column.controls.append(job_button)
        else:
            job_recommendation_column.controls.append(ft.Text("No matching jobs found."))

        page.update()

    skill_input = ft.TextField(label="Enter Skill")
    job_role_input = ft.TextField(label="Optional: Enter Job Role")
    recommend_button = ft.ElevatedButton("Recommend Jobs", on_click=recommend_jobs)

    job_recommendation_tab = ft.Column([
        ft.Container(ft.Text("Job Recommendation", size=20), alignment=ft.alignment.center),
        skill_input,
        job_role_input,
        recommend_button,
        job_recommendation_column
    ], spacing=15, visible=False)

    # ============================ Chatbot Tab ============================
    chatbot_output = ft.Column()
    chatbot_input = ft.TextField(label="Ask me anything...", expand=True)
    
    def send_message(e):
        user_message = chatbot_input.value.strip()
        if not user_message:
            return

        chatbot_output.controls.append(ft.Text(f"You: {user_message}", weight=ft.FontWeight.BOLD))
        chatbot_input.value = ""
        page.update()

        response = chatbot.get_response(user_message)
        chatbot_output.controls.append(ft.Text(f"AI: {response}"))
        page.update()

    chatbot_send_button = ft.ElevatedButton("Send", on_click=send_message)

    chatbot_tab = ft.Column([
        ft.Container(ft.Text("AI Chatbot", size=20), alignment=ft.alignment.center),
        chatbot_output,
        ft.Row([chatbot_input, chatbot_send_button])
    ], spacing=15, visible=False)

    # ============================ Tab Management ============================
    tab_contents = [resume_tab, job_recommendation_tab, chatbot_tab]

    bottom_app_bar = ft.BottomAppBar(
        content=ft.Row(
            [
                ft.TextButton("Resume Analysis", on_click=lambda e: show_tab(0)),
                ft.TextButton("Job Recommendation", on_click=lambda e: show_tab(1)),
                ft.TextButton("Chatbot", on_click=lambda e: show_tab(2))
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        ),
        elevation=10,
        visible=True
    )

    page.bottom_appbar = bottom_app_bar
    page.add(resume_tab, job_recommendation_tab, chatbot_tab)

ft.app(target=main)
