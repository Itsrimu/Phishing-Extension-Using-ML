# Phishing Detection Browser Extension using Machine Learning

A cross-browser extension and backend system that detects phishing URLs in real time using a trained machine learning model.  
Users can check, report, and give feedback on suspicious sites, helping improve the detection system.

---

## 🚀 Features

- **Real-time Phishing Detection:**  
  Checks the current page or any hovered link for phishing risks using a trained ML model.
- **User Feedback:**  
  Users can mark sites as phishing or legitimate, improving the system.
- **Phishing Reporting:**  
  Report suspicious URLs directly from the extension.
- **Settings Sync:**  
  Auto-detection toggle and other settings are synced between popup and content scripts.
- **Batch Prediction API:**  
  Backend supports batch URL analysis.
- **Short Link Expansion:**  
  Extension expands shortened URLs for transparency.
- **Accessible UI:**  
  Designed for clarity and accessibility.

---

## 🏗️ Project Structure

GitHub Copilot
Certainly! Here’s a README-style section you can copy directly into your README.md, using clear Markdown formatting and highlighting your notebook-based analysis and findings:

📓 **Notebook Analysis & Experiments**
We conducted extensive experiments using Jupyter Notebooks to analyze multiple phishing datasets and evaluate different machine learning algorithms. Our workflow and findings are summarized below:
---
### 🔬 Experiment Approaches
1. Without Feature Engineering
Method:
Used raw dataset columns as direct input to machine learning models, without extracting or engineering any additional features.
Result:
All tested algorithms (Random Forest, Logistic Regression, SVM, etc.) performed poorly.
Models showed low accuracy and struggled to distinguish phishing from legitimate URLs.
2. With Feature Engineering
Method:
Extracted meaningful features from URLs (e.g., length, use of special characters, presence of HTTPS, number of subdomains, etc.) and used these as model input.
Result:
All algorithms performed significantly better.
Random Forest achieved the highest accuracy and reliability.
Feature-based models were much more robust and effective at phishing detection.
---
### 🏆Key Findings
Feature engineering is essential for effective phishing detection using machine learning.
Random Forest with engineered features provided the best results in our experiments.
Models trained without feature extraction were much less accurate and not suitable for real-world use.

### 📁 How to Reproduce
Open the Jupyter Notebooks in the backend directory (e.g., phishing_analysis.ipynb).
Follow the step-by-step workflow for:
Data exploration
Feature extraction
Model training and evaluation
You can use your own datasets by following the same process.

### 🔗 Example Notebook
See backend/phishing_analysis.ipynb for the full experimental workflow and results.

**These experiments guided our decision to use feature-based Random Forest models in the extension backend for the most accurate phishing detection.**

```
browserExtention/
│
├── backend/
│   ├── main.py                # Flask app entry point
│   ├── predict.py             # Prediction logic
│   ├── train_model.py         # Model training script
│   ├── features.py            # Feature extraction
│   ├── database.py            # MongoDB operations
│   ├── routes/
│   │   ├── predict_routes.py
│   │   └── feedback_routes.py
│   ├── model/                 # Trained model files (.pkl)
│   ├── data/                  # (Ignored) Raw datasets
│   └── logs/                  # Log files
│
├── extention/
│   ├── popup.html             # Extension popup UI
│   ├── popup.js               # Popup logic
│   ├── content.js             # Content script (hover, banners, etc.)
│   ├── background.js          # Background script
│   ├── settings.html          # Settings page
│   ├── icons/                 # Extension icons
│   ├── manifest.json          # Extension manifest
│   └── .gitignore
│
└── README.md                  # This file
```

---

## ⚙️ Setup Instructions

### 1. **Clone the Repository**

```sh
git clone https://github.com/Itsrimu/Phishing-Extension-Using-ML.git
cd Phishing-Extension-Using-ML
```

### 2. **Backend Setup**

- **Python 3.8+** required.
- Install dependencies:
  ```sh
  cd backend
  python -m venv venv
  venv\Scripts\activate  # On Windows
  pip install -r requirements.txt
  ```
- **MongoDB** must be running (local or Atlas).
- **Train the model** (if not already trained):
  ```sh
  python train_model.py
  ```
- **Start the Flask server:**
  ```sh
  python main.py
  ```
  The API will be available at `http://127.0.0.1:5000/`.

### 3. **Extension Setup**

- Go to `chrome://extensions` (or your browser’s extension page).
- Enable "Developer mode".
- Click "Load unpacked" and select the `extention/` folder.
- The extension icon should appear in your browser.

---

## 🧑‍💻 Usage

- **Check Current URL:**  
  Click the extension icon and use "Check Current URL".
- **Hover Detection:**  
  Hover any link to see if it’s safe or unsafe (tooltip appears).
- **Report Phishing:**  
  Use the "Report Phishing" button in the popup or right-click a link.
- **Feedback:**  
  Mark a site as phishing or legitimate to help improve detection.
- **Settings:**  
  Toggle auto-detection and other options in the popup.

---

## 🛡️ Security & Privacy

- **No secrets or sensitive data are stored in the repository.**
- All secrets (API keys, datasets) are excluded via `.gitignore`.
- If you contribute, **never commit secrets or credentials**.

---

## 📝 API Endpoints (Backend)

- `POST /api/predict-only`  
  `{ "url": "https://..." }` → `{ "analysis_result": "Phishing"|"Legitimate", "confidence": "...%" }`
- `POST /api/feedback`  
  `{ "url": "...", "feedback": "yes|no|not_sure" }`
- `POST /api/feedback/report`  
  `{ "url": "...", "reason": "..." }`
- `GET /api/feedback/reported_phishing`  
  Returns reported URLs for retraining.

---

## 🧩 Contributing

1. Fork the repo and create your branch.
2. Make your changes.
3. Ensure you **do not commit secrets or large data files**.
4. Submit a pull request!

---

## 📄 License

[MIT License](LICENSE)

---


## ⭐ Credits

KHAIRUN NESSA NAZMIN


---

**Enjoy safer browsing!**
