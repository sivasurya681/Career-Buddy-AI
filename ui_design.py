import flet as ft
import prediction
import resume_parser
import chatbot
import pandas as pd
import os
import webbrowser

# Load dataset
if not os.path.exists("dataset_clean.csv"):
    print("Error: dataset_clean.csv not found!")
    df = None
else:
    df = pd.read_csv("dataset_clean.csv")
    df.columns = df.columns.str.lower()

# Helper to open URL
def open_url(url):
    return lambda e: webbrowser.open(url)

def fallback_linkedin_jobs(skill_text, num_links=5):
    return prediction.get_linkedin_job_links(skill_text, num_links=num_links)

recent_searches = []

def add_recent_search(query):
    if query not in recent_searches:
        recent_searches.append(query)
        if len(recent_searches) > 5:
            recent_searches.pop(0)

def get_skill_suggestions(query):
    query = query.lower()
    return [s for s in skill_suggestions if query in s.lower()][:5]

def main(page: ft.Page):
    page.title = "CareerBuddy - AI"
    page.scroll = ft.ScrollMode.ALWAYS
    page.theme_mode = "light"

    def get_text_color():
        return ft.Colors.BLACK if page.theme_mode == "light" else ft.Colors.WHITE

    def update_all_text_colors():
        text_elements = [
            header_title, prediction_result_text,
            skills_field, role_field, chatbot_field, job_heading,
            chatbot_heading, resume_heading, banner_text
        ]
        for element in text_elements:
            element.color = get_text_color()
        skills_field.text_style = ft.TextStyle(color=get_text_color())
        role_field.text_style = ft.TextStyle(color=get_text_color())
        chatbot_field.text_style = ft.TextStyle(color=get_text_color())

    def toggle_theme(e):
        page.theme_mode = "dark" if page.theme_mode == "light" else "light"
        update_all_text_colors()
        page.update()

    def show_tab(index):
        for i, content in enumerate(tab_contents):
            content.visible = i == index
        page.update()

    theme_switch = ft.Switch(label="🌙", value=False, on_change=toggle_theme)
    header_title = ft.Text("🚀 Empowering your career journey with AI!", size=18, italic=True, color=get_text_color())
    header = ft.Row([header_title, theme_switch], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    banner_text = ft.Text("💼 CareerBuddy - AI", size=30, weight="bold", expand=True, color=get_text_color())
    banner = ft.Container(banner_text, alignment=ft.alignment.center, padding=10)

    global skills_field, skill_suggestions, suggestion_list
    skill_suggestions = ["Python", "Data Science", "Machine Learning", "Deep Learning", "JavaScript", "SQL", "Java", "HTML", "CSS", "Node.js"]
    suggestion_list = ft.Column(visible=False, spacing=0)

    def select_suggestion(skill):
        skills_field.value = skill
        suggestion_list.visible = False
        page.update()

    def update_suggestion_list():
        typed = skills_field.value.strip().lower()
        matches = get_skill_suggestions(typed)
        suggestion_list.controls.clear()
        if typed and matches:
            for skill in matches:
                suggestion_list.controls.append(
                    ft.TextButton(
                        text=skill,
                        on_click=lambda e, s=skill: select_suggestion(s),
                        style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=20), color=get_text_color())
                    )
                )
            suggestion_list.visible = True
        else:
            suggestion_list.visible = False
        page.update()

    skills_field = ft.TextField(label="Enter your skills", width=350, on_change=lambda e: update_suggestion_list(), autofocus=True, color=get_text_color(), text_style=ft.TextStyle(color=get_text_color()))
    role_field = ft.TextField(label="Enter job role (optional)", width=350, color=get_text_color(), text_style=ft.TextStyle(color=get_text_color()))

    prediction_result_text = ft.Text(color=get_text_color())
    prediction_result_container = ft.Column()
    prediction_loader = ft.Row([ft.ProgressRing(), ft.Text("Predicting job titles...", size=14)], visible=False, alignment=ft.MainAxisAlignment.CENTER)

    def predict_click(e):
        skills = skills_field.value
        role = role_field.value
        if not skills:
            prediction_result_text.value = "Error: Skills are mandatory"
            page.update()
            return

        prediction_loader.visible = True
        prediction_result_text.value = ""
        prediction_result_container.controls.clear()
        page.update()

        input_text = (role + " " if role else "") + skills
        preds = prediction.predict_job_titles(input_text)

        prediction_loader.visible = False
        prediction_result_container.controls.clear()

        if not preds or preds[0][1] < 0.2:
            prediction_result_text.value = "Skill match not found. But here are jobs from LinkedIn!"
            fallback_links = fallback_linkedin_jobs(input_text)
            for i, link in enumerate(fallback_links):
                prediction_result_container.controls.append(
                    ft.ElevatedButton(
                        text=f"🔗 Apply for '{input_text.strip().title()}' on LinkedIn #{i+1}",
                        on_click=open_url(link),
                        style=ft.ButtonStyle(bgcolor=ft.Colors.YELLOW)
                    )
                )
        else:
            for title, prob in preds:
                title_lower = title.lower()
                companies = df[df["job title"].str.lower().str.contains(title_lower, na=False)]["company"].drop_duplicates().tolist() if df is not None else []
                linkedin_links = prediction.get_linkedin_job_links(title, num_links=1)
                job_link_button = ft.ElevatedButton(
                    text=f"🔗 Apply for {title} on LinkedIn",
                    on_click=open_url(linkedin_links[0]),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN)
                ) if linkedin_links else None

                block = [
                    ft.Text(f"{title} (Confidence: {prob:.2f})", size=18, color=get_text_color(), weight="bold"),
                    ft.Text(f"Companies: {', '.join(companies[:5])}", color=get_text_color())
                ]
                if job_link_button:
                    block.append(job_link_button)

                prediction_result_container.controls.append(
                    ft.Card(content=ft.Container(ft.Column(block), padding=10), elevation=5)
                )
        page.update()

    # Elevated Button for prediction
    predict_button = ft.ElevatedButton("🔍 Predict Job Titles", on_click=predict_click, style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE))
    # Handle Enter key press for prediction
    skills_field.on_submit = predict_click

    job_heading = ft.Text("🧠 Job Prediction", size=20, weight="bold", color=get_text_color())
    job_tab = ft.Column([ft.Container(job_heading, alignment=ft.alignment.center),
                         ft.Container(ft.Row([skills_field, role_field], alignment=ft.MainAxisAlignment.CENTER, spacing=20)),
                         ft.Container(suggestion_list, padding=ft.padding.only(left=30)),
                         ft.Container(ft.Row([predict_button], alignment=ft.MainAxisAlignment.CENTER)),
                         prediction_loader,
                         prediction_result_text,
                         prediction_result_container
                         ], spacing=15, visible=True)

    # === Chatbot ===
    chatbot_field = ft.TextField(label="Ask your career question", width=350, color=get_text_color(), text_style=ft.TextStyle(color=get_text_color()))
    chatbot_result_column = ft.Column(spacing=5, scroll=ft.ScrollMode.ADAPTIVE)
    chatbot_loader = ft.Row([ft.ProgressRing(), ft.Text("Chatbot is processing...", size=14)], visible=False, alignment=ft.MainAxisAlignment.CENTER)

    def chatbot_click(e):
        query = chatbot_field.value
        if not query:
            chatbot_result_column.controls.clear()
            chatbot_result_column.controls.append(ft.Text("Error: Please enter a query", size=16, color=ft.Colors.RED))
            page.update()
            return

        chatbot_loader.visible = True
        chatbot_result_column.controls.clear()
        page.update()

        responses = chatbot.get_chatbot_response(query)
        chatbot_loader.visible = False
        chatbot_result_column.controls.extend(responses)
        page.update()

    # Elevated Button for chatbot
    chatbot_button = ft.ElevatedButton("💬 Ask Chatbot", on_click=chatbot_click, style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE))
    # Handle Enter key press for chatbot
    chatbot_field.on_submit = chatbot_click

    chatbot_heading = ft.Text("🤖 Career Chatbot", size=20, weight="bold", color=get_text_color())
    chatbot_tab = ft.Column([ft.Container(chatbot_heading, alignment=ft.alignment.center),
                             ft.Container(ft.Row([chatbot_field], alignment=ft.MainAxisAlignment.CENTER)),
                             ft.Container(ft.Row([chatbot_button], alignment=ft.MainAxisAlignment.CENTER)),
                             chatbot_loader,
                             chatbot_result_column
                             ], spacing=15, visible=False)

    # === Resume Analysis ===
    resume_result_container = ft.Column()
    resume_loader = ft.Row([ft.ProgressRing(), ft.Text("Parsing resume...", size=14)], visible=False, alignment=ft.MainAxisAlignment.CENTER)

    def resume_picker_result(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            resume_loader.visible = True
            resume_result_container.controls.clear()
            page.update()

            resume_info = resume_parser.parse_resume(file_path)
            resume_loader.visible = False

            extracted_skills = resume_info.get("extracted_skills", "").split(",")
            matched_jobs = resume_info.get("matched_jobs", {})

            if extracted_skills:
                resume_result_container.controls.append(ft.Text("Extracted Skills:", size=16, weight="bold", color=get_text_color()))
                for skill in extracted_skills[:5]:
                    resume_result_container.controls.append(ft.Text(f"🔹 {skill.strip()}", color=get_text_color()))
                resume_result_container.controls.append(ft.Text("\nSuggested Jobs:", size=16, weight="bold", color=get_text_color()))
                for skill, link in matched_jobs.items():
                    resume_result_container.controls.append(ft.ElevatedButton(text=f"{skill} - LinkedIn Job", on_click=open_url(link)))
            else:
                resume_result_container.controls.append(ft.Text("No skills found.", color=get_text_color()))
        else:
            resume_result_container.controls.append(ft.Text("No file selected.", color=get_text_color()))
        page.update()

    file_picker = ft.FilePicker(on_result=resume_picker_result)
    page.overlay.append(file_picker)

    upload_resume_button = ft.ElevatedButton("📄 Upload Resume", on_click=lambda e: file_picker.pick_files(), style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE))
    resume_heading = ft.Text("📎 Resume Analysis", size=20, weight="bold", color=get_text_color())
    resume_tab = ft.Column([ft.Container(resume_heading, alignment=ft.alignment.center),
                            ft.Container(ft.Row([upload_resume_button], alignment=ft.MainAxisAlignment.CENTER)),
                            resume_loader,
                            resume_result_container
                            ], spacing=15, visible=False)

    # === Tabs & Footer ===
    tab_contents = [job_tab, chatbot_tab, resume_tab]
    bottom_app_bar = ft.BottomAppBar(
        content=ft.Column([ft.Row([ft.TextButton("🧠 Job Prediction", on_click=lambda e: show_tab(0)),
                                  ft.TextButton("🤖 Chatbot", on_click=lambda e: show_tab(1)),
                                  ft.TextButton("📎 Resume Analysis", on_click=lambda e: show_tab(2))
                                  ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                            ft.Divider(),
                            ft.Row([ft.Text("© 2025 CareerBuddy - AI | Connect: ", color=ft.Colors.GREY),
                                    ft.TextButton("LinkedIn", on_click=open_url("https://www.linkedin.com")),
                                    ft.TextButton("GitHub", on_click=open_url("https://www.github.com"))
                                    ], alignment=ft.MainAxisAlignment.CENTER)
                            ])
    )

    page.bottom_appbar = bottom_app_bar
    page.add(ft.Column([banner, header] + tab_contents, spacing=25, scroll=ft.ScrollMode.ALWAYS))

ft.app(target=main)
