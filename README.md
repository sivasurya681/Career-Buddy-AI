# CareerBuddy-AI  
AI-powered career assistance application that helps job seekers with **resume parsing**, **job recommendations**, **company search**, and **career guidance** using Machine Learning and Web Scraping.

## Project Description:  
CareerBuddy AI is designed to streamline the job search process for candidates by leveraging **Machine Learning**, **Natural Language Processing (NLP)**, and **Web Scraping**.  
The app can take user input (skills and/or job role) or parse a resume to extract skills, predict suitable job titles, recommend companies, and fetch real-time job links from portals like LinkedIn and Naukri.  
It also features an interactive chatbot for career-related queries and guidance.

## Features:
- Resume parsing to automatically extract skills.
- Job title prediction using Machine Learning models.
- Real-time company and job link recommendations from job portals.
- Interactive chatbot for career advice.
- Skill gap analysis with learning resource suggestions.
- Professional multi-section UI built with Flet.

## Running the app:
Flet + Flask:  
- Run <code>pip install -r requirements.txt</code> to install all dependencies.  
- Ensure the dataset (CSV) is in the `data/` directory with required columns (Qualifications, Salary Range, Job Title, Role, Job Description, Skills, Company).  
- Run <code>python train.py</code> to train the XGBoost model if not already trained.  
- Run <code>python main.py</code> to start the application.

## Tech Stack:
- Python  
- Flet (Frontend)  
- Flask (Backend API)  
- XGBoost, Scikit-learn (ML Models)  
- NLP (spaCy / Transformers)  
- BeautifulSoup, Requests (Web Scraping)  
- Pandas, Matplotlib (Data Handling & Visualization)  

## Dataset:
The dataset contains job-related fields such as:  
- Qualifications  
- Salary Range  
- Job Title  
- Role  
- Job Description  
- Skills  
- Company  

**Note:** Dataset should be cleaned and preprocessed before training for better accuracy.

## Model Architecture:
- **ML Algorithm:** XGBoost for job title prediction.  
- **Input:** Skills (from user or resume parsing).  
- **Output:** Recommended job titles & matching companies.  
- Web Scraping layer fetches job links for the recommended roles.  
- Chatbot integrated using NLP to provide career guidance.

## Data Processing and Training:
- Skills are extracted from text input or resume using NLP.  
- Job titles and companies are matched using dataset filtering + ML predictions.  
- The XGBoost model is trained on preprocessed CSV data.  

## Current Condition:
The application is fully functional:  
- Resume parsing, job title prediction, and job link scraping work as expected.  
- Chatbot provides relevant career responses.  
- UI is clean, responsive, and divided into three sections for better user experience.

## Project Components:
- `train.py` – Trains the XGBoost model on the dataset.  
- `main.py` – Runs the Flet application (UI + Backend Integration).  
- `test.py` – Tests the model predictions and WHOIS-based phishing detection (if integrated).  
- `models/` – Stores trained ML models.  
- `data/` – Contains dataset files.  
- `templates/` – HTML files if web views are used.  
- `requirements.txt` – List of dependencies.
