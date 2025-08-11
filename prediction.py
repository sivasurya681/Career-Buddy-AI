import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
import joblib
import requests
from bs4 import BeautifulSoup

MODEL_FILENAME = "model.joblib"


def train_model():
    if os.path.exists("dataset_clean.csv"):
        df = pd.read_csv("dataset_clean.csv")
    else:
        df = pd.read_csv("dataset.csv")
    
    if "role" in df.columns and "skills" in df.columns:
        df["text_features"] = df["role"].fillna('') + " " + df["skills"].fillna('')
    else:
        raise KeyError("Dataset must contain 'role' and 'skills' columns.")
    
    X = df["text_features"]
    y = df["job title"]
    
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline = make_pipeline(
        TfidfVectorizer(),
        LogisticRegression(max_iter=1000)
    )
    
    pipeline.fit(X_train, y_train)
    joblib.dump(pipeline, MODEL_FILENAME)
    print(f"Model trained and saved as '{MODEL_FILENAME}'.")


def predict_job_titles(input_text, top_n=5):
    pipeline = joblib.load(MODEL_FILENAME)
    probs = pipeline.predict_proba([input_text])[0]
    job_titles = pipeline.classes_
    job_prob_pairs = sorted(zip(job_titles, probs), key=lambda x: x[1], reverse=True)
    return job_prob_pairs[:top_n]


def get_linkedin_job_links(job_title, num_links=5):
    search_url = f"https://www.linkedin.com/jobs/search?keywords={job_title.replace(' ', '%20')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    job_links = []
    
    for job in soup.find_all("a", class_="base-card__full-link", href=True):
        job_links.append(job["href"])
        if len(job_links) >= num_links:
            break
    
    return job_links


if __name__ == "__main__":
    train_model()