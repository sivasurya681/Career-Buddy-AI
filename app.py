from flask import Flask, request, jsonify
import joblib
import prediction
import resume_parser
import chatbot
import pandas as pd
import re
import web_scraper  # New module for web scraping

app = Flask(__name__)

# Load dataset for job link retrieval and ensure column names are lowercase.
print("Loading dataset for API endpoints...")
df = pd.read_csv(r"F:\Intern Project\Final Code\dataset_clean.csv")
df.columns = df.columns.str.lower()
print("Dataset loaded.")

@app.route("/predict-job", methods=["POST"])
def predict_job():
    data = request.get_json()
    skills = data.get("skills", "")
    role = data.get("role", "")
    if not skills:
        return jsonify({"error": "Skills are mandatory"}), 400
    input_text = (role + " " if role else "") + skills
    preds = prediction.predict_job_titles(input_text)
    if preds[0][1] < 0.2:
        return jsonify({"message": "Upgrade your skill"}), 200
    results = []
    for title, prob in preds:
        title_lower = title.lower()
        matching = df[df["job title"].str.contains(re.escape(title_lower), case=False, na=False)]
        companies = matching["company"].drop_duplicates().tolist()
        job_links = web_scraper.scrape_job_links(title)  # Scrape job links
        results.append({
            "job_title": title,
            "confidence": prob,
            "companies": companies[:10],
            "job_links": job_links
        })
    return jsonify({"predictions": results})

@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    file_path = "temp_resume." + file.filename.split(".")[-1]
    file.save(file_path)
    resume_info = resume_parser.parse_resume(file_path)
    return jsonify(resume_info)

@app.route("/chatbot", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "")
    response = chatbot.get_chatbot_response(query)
    return jsonify({"response": response})

if __name__ == "__main__":
    print("Starting Flask backend on port 5000...")
    app.run(debug=True, port=5000)
