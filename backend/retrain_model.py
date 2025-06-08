# File: backend/retrain_model.py

import pandas as pd
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV
from feature import extract_url_features
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import classification_report, accuracy_score

# Paths
MAIN_DATA_PATH = Path("data/phishing_site_urls.csv")
FEEDBACK_DATA_PATH = Path("data/phishing_feedback.csv")  # Separate feedback file
MODEL_DIR = Path("model")
MODEL_PATH = MODEL_DIR / "phishing_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "vectorizer.pkl"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

def is_valid_url(url):
    try:
        if not isinstance(url, str) or not url.strip():
            return False
        _ = extract_url_features(url)
        return True
    except Exception:
        return False

def retrain_model_with_feedback(new_url: str, feedback: str):
    if feedback not in ['good', 'bad']:
        raise ValueError("Feedback must be 'good' or 'bad'.")

    try:
        new_features = extract_url_features(new_url)
    except Exception as e:
        raise ValueError(f"Invalid URL: {e}")

    new_label = 0 if feedback == 'good' else 1

    # Load main dataset
    main_df = pd.read_csv(MAIN_DATA_PATH)
    main_df = main_df[['URL', 'Label']].dropna()
    main_df['Label'] = main_df['Label'].map({'good': 0, 'bad': 1})

    # Load or create feedback dataset
    if FEEDBACK_DATA_PATH.exists():
        feedback_df = pd.read_csv(FEEDBACK_DATA_PATH)
    else:
        feedback_df = pd.DataFrame(columns=["URL", "Label"])

    # Append new feedback entry
    new_entry = pd.DataFrame({"URL": [new_url], "Label": [new_label]})
    feedback_df = pd.concat([feedback_df, new_entry], ignore_index=True)
    feedback_df.to_csv(FEEDBACK_DATA_PATH, index=False)

    # Combine datasets
    combined_df = pd.concat([main_df, feedback_df], ignore_index=True)

    # Filter valid URLs and extract features
    combined_df = combined_df[combined_df['URL'].apply(is_valid_url)]
    combined_df['features'] = combined_df['URL'].apply(lambda u: extract_url_features(u))

    X_train, X_test, y_train, y_test = train_test_split(
        combined_df['features'].tolist(), combined_df['Label'],
        test_size=0.2, random_state=42, stratify=combined_df['Label']
    )

    pipeline = Pipeline([
        ("vectorizer", DictVectorizer(sparse=False)),
        ("classifier", RandomForestClassifier(random_state=42))
    ])

    param_grid = {
        "classifier__n_estimators": [100, 150],
        "classifier__max_depth": [None, 10, 20]
    }

    grid = GridSearchCV(pipeline, param_grid, cv=5, scoring='f1', verbose=1, n_jobs=-1)
    grid.fit(X_train, y_train)

    y_pred = grid.predict(X_test)
    print("\nUpdated Model Accuracy:", accuracy_score(y_test, y_pred))
    print("\nUpdated Classification Report:\n", classification_report(y_test, y_pred))

    best_model = grid.best_estimator_
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(best_model, f)

    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(best_model.named_steps["vectorizer"], f)

    print(f"\nUpdated model saved at {MODEL_PATH}")
    print(f"Updated vectorizer saved at {VECTORIZER_PATH}")
