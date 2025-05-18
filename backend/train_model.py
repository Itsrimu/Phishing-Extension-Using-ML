# File: backend/train_model.py

import pandas as pd
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import classification_report, accuracy_score
from feature import extract_url_features

# Paths
DATA_PATH = Path("data/phishing_site_urls.csv")
MODEL_DIR = Path("model")
MODEL_PATH = MODEL_DIR / "phishing_model1.pkl"
VECTORIZER_PATH = MODEL_DIR / "vectorizer1.pkl"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Load and preprocess dataset
df = pd.read_csv(DATA_PATH)
df = df[['URL', 'Label']].dropna()
df['Label'] = df['Label'].map({'good': 0, 'bad': 1})

# Filter out invalid URLs
def is_valid_url(url):
    try:
        if not isinstance(url, str) or url.strip() == "":
            return False
        _ = extract_url_features(url)
        return True
    except Exception:
        return False

df = df[df['URL'].apply(is_valid_url)]

# Feature extraction
df['features'] = df['URL'].apply(extract_url_features)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    df['features'].tolist(), df['Label'], test_size=0.2, random_state=42, stratify=df['Label']
)

# Define pipeline
pipeline = Pipeline([
    ("vectorizer", DictVectorizer(sparse=False)),
    ("classifier", RandomForestClassifier(random_state=42))
])

# Grid search
param_grid = {
    "classifier__n_estimators": [100, 150],
    "classifier__max_depth": [None, 10, 20]
}
grid = GridSearchCV(pipeline, param_grid, cv=5, scoring='f1', verbose=1, n_jobs=-1)
grid.fit(X_train, y_train)

# Evaluate
y_pred = grid.predict(X_test)
print("\n Best Parameters:", grid.best_params_)
print("\n Accuracy:", accuracy_score(y_test, y_pred))
print("\n Classification Report:\n", classification_report(y_test, y_pred))

# Save best model and vectorizer
best_model = grid.best_estimator_
with open(MODEL_PATH, "wb") as f:
    pickle.dump(best_model, f)

with open(VECTORIZER_PATH, "wb") as f:
    pickle.dump(best_model.named_steps['vectorizer'], f)

print(f"\n Model saved at {MODEL_PATH}")
print(f" Vectorizer saved at {VECTORIZER_PATH}")

# Update model from feedback
def update_model_with_feedback(new_url: str, feedback: str):
    """
    Update the model using a new URL and feedback ('good' or 'bad'). 
    Retrains the model and saves updated version.
    """
    if feedback not in ["good", "bad"]:
        raise ValueError("Feedback must be 'good' or 'bad'.")

    try:
        new_features = extract_url_features(new_url)
    except Exception as e:
        raise ValueError(f"Invalid URL format: {new_url}") from e

    new_label = 0 if feedback == "good" else 1

    # Load current data from disk (to persist feedback)
    current_data = pd.read_csv(DATA_PATH)
    current_data = current_data[['URL', 'Label']].dropna()
    current_data['Label'] = current_data['Label'].map({'good': 0, 'bad': 1})

    # Append new data
    new_entry = pd.DataFrame({
        "URL": [new_url],
        "Label": [new_label]
    })
    updated_df = pd.concat([current_data, new_entry], ignore_index=True)

    # Save updated dataset
    updated_df.to_csv(DATA_PATH, index=False)

    # Filter and re-extract
    updated_df = updated_df[updated_df['URL'].apply(is_valid_url)]
    updated_df['features'] = updated_df['URL'].apply(extract_url_features)

    # Retrain with updated data
    X_train, X_test, y_train, y_test = train_test_split(
        updated_df['features'].tolist(), updated_df['Label'],
        test_size=0.2, random_state=42, stratify=updated_df['Label']
    )

    grid.fit(X_train, y_train)
    y_pred = grid.predict(X_test)

    print("\n Updated Accuracy:", accuracy_score(y_test, y_pred))
    print("\n Updated Classification Report:\n", classification_report(y_test, y_pred))

    # Save updated model and vectorizer
    updated_model = grid.best_estimator_
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(updated_model, f)

    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(updated_model.named_steps['vectorizer'], f)

    print(f"\n Updated model saved at {MODEL_PATH}")
    print(f" Updated vectorizer saved at {VECTORIZER_PATH}")
