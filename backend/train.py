# File: train_model.py

import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.base import BaseEstimator, TransformerMixin

from feature import extract_features, url_tokenizer

# Load dataset
DATA_PATH = Path("data/phishing_site_urls.csv")
MODEL_PATH = Path("model/phishing_model_combined.pkl")
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)
df = df[['URL', 'Label']].dropna()
df['Label'] = df['Label'].map({'good': 0, 'bad': 1})

# Extract features
df_features = df['URL'].apply(lambda x: pd.Series(extract_features(x)))
df_final = pd.concat([df, df_features], axis=1)

# Split into components
X_text = df_final['URL']
X_numeric = df_features
y = df_final['Label']

X_text_train, X_text_test, X_num_train, X_num_test, y_train, y_test = train_test_split(
    X_text, X_numeric, y, test_size=0.2, random_state=42, stratify=y
)

# Final training and test frames
X_train_combined = pd.concat([X_text_train.reset_index(drop=True), X_num_train.reset_index(drop=True)], axis=1)
X_test_combined = pd.concat([X_text_test.reset_index(drop=True), X_num_test.reset_index(drop=True)], axis=1)
X_train_combined.columns = ['url'] + list(X_numeric.columns)
X_test_combined.columns = ['url'] + list(X_numeric.columns)

# Custom passthrough transformer for numeric features
class ManualFeatures(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X): return X

# Preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('text', CountVectorizer(tokenizer=url_tokenizer, stop_words='english'), 'url'),
        ('num', Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('manual', ManualFeatures())
        ]), list(X_numeric.columns))
    ]
)

pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(solver='liblinear'))
])

# Train
pipeline.fit(X_train_combined, y_train)

# Evaluate
print("Training Accuracy:", pipeline.score(X_train_combined, y_train))
print("Testing Accuracy:", pipeline.score(X_test_combined, y_test))

# Save the model
with open("model/phishing_model_combined.pkl", "wb") as f:
    joblib.dump(pipeline, f)

print(f"Model saved to {MODEL_PATH}")
