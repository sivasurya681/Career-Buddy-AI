import pandas as pd
import spacy

def preprocess_text(text, nlp):
    """Tokenize, lemmatize, and remove punctuation."""
    if not isinstance(text, str):
        return ""
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if not token.is_punct and not token.is_space]
    return " ".join(tokens)

def standardize_column(text, mapping):
    """Replace text based on a mapping dictionary."""
    if not isinstance(text, str):
        return ""
    return mapping.get(text.lower().strip(), text.lower().strip())

def main():
    print("Starting data preparation...")
    
    # Load dataset
    dataset_path = "F:\\Intern Project\\Final Code\\dataset_clean.csv"  # Update path
    print(f"Loading dataset from '{dataset_path}'...")
    df = pd.read_csv(dataset_path)
    print(f"✅ Dataset loaded with {len(df)} rows.")

    # Print available columns
    print("🔍 Available columns:", df.columns.tolist())

    # Remove duplicates
    print("Removing duplicates...")
    df.drop_duplicates(inplace=True)
    print(f"✅ Rows after duplicate removal: {len(df)}")

    # Handle missing columns
    required_columns = ["Qualifications", "Salary Range", "Job Title", "Role", "Job Description", "Skills", "Company"]
    existing_columns = [col for col in required_columns if col in df.columns]

    if "Skills" not in df.columns:
        print("⚠ Warning: 'Skills' column not found. Checking for alternatives...")
        possible_alternatives = ["Skill", "Skill Set", "Technical Skills"]
        for alt in possible_alternatives:
            if alt in df.columns:
                print(f"✅ Found alternative column: {alt} → Renaming to 'Skills'")
                df.rename(columns={alt: "Skills"}, inplace=True)
                existing_columns.append("Skills")
                break

    if existing_columns:
        print(f"Dropping rows with missing values in columns: {existing_columns}")
        df.dropna(subset=existing_columns, inplace=True)
        print(f"✅ Rows after dropping missing values: {len(df)}")
    else:
        print("⚠ No matching columns found to drop NaN values!")

    # Convert text columns to lowercase
    print("Converting key columns to lowercase...")
    for col in ["Qualifications", "Job Title", "Role", "Job Description", "Skills", "Company"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower()

    # Initialize spaCy
    print("Loading spaCy model...")
    nlp = spacy.load("en_core_web_sm")

    # Tokenization & Lemmatization
    print("Tokenizing and lemmatizing 'Job Description' column...")
    if "Job Description" in df.columns:
        df["Job Description"] = df["Job Description"].apply(lambda x: preprocess_text(x, nlp))

    # Save cleaned dataset
    output_file = "dataset_clean.csv"
    df.to_csv(output_file, index=False)
    print(f"✅ Data preparation complete. Cleaned dataset saved as '{output_file}'.")

if __name__ == "__main__":
    main()
