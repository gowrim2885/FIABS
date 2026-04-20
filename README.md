# FIABS – Fiscal Intelligence & Adaptive Budgeting System

FIABS is a state-of-the-art fiscal management and forecasting platform designed to provide governments, analysts, and the public with AI-driven insights into economic data. By combining deep learning (LSTM) for GDP forecasting, MCDM for resource allocation, and a secure role-based access system, FIABS transforms raw fiscal data into actionable strategic intelligence.

## 🌟 Features

- **Recursive GDP Forecasting**: Uses an LSTM neural network to predict GDP trends up to 5 years into the future, with recursive feedback (t+1 used as input for t+2).
- **AI-Powered Resource Allocation**: Utilizes Multi-Criteria Decision Making (MCDM) to rank departmental budget requests based on ROI, Impact, and Risk.
- **Anomaly Detection**: Automatically flags "Abnormal Spending" in fiscal datasets using Isolation Forest models.
- **Role-Based Access Control (RBAC)**: Secure entry for **Policy Makers** (Strategic KPIs), **Analysts** (Data Upload/Training), and **Public Viewers** (Transparency Dashboard).
- **Custom JWT Authentication**: Robust, dependency-free JWT implementation for secure session management.
- **Dual-Theme Support**: Professional Dark/Light mode with persistence using `localStorage`.
- **Interactive Chatbot**: Integrated AI assistant for natural language queries about fiscal data.

---

## 📂 Project Structure

```text
FIABS/
├── data/                   # Fiscal datasets (Raw and Processed)
│   ├── raw/                # Original CSV files (GDP, Inflation, etc.)
│   ├── processed/          # Cleaned and merged datasets for training
│   └── users.db            # SQLite database for user credentials
├── frontend/               # Web interface (HTML/CSS/JS)
│   ├── css/                # Styling (Inter font, Responsive layouts)
│   ├── js/                 # Logic (login.js, app.js, session.js)
│   ├── public/             # Public-facing dashboard
│   ├── index.html          # Enterprise Dashboard (Policy/Analyst)
│   └── login.html          # Secure minimalist login portal
├── ml_api/                 # FastAPI Backend
│   ├── routes/             # API Endpoints (Auth, Predict, Analyst, Public)
│   ├── services/           # Business logic (LSTM engine, MCDM, Chatbot)
│   └── app.py              # Main application entry point (Port 8001)
├── model/                  # Trained machine learning models
│   ├── gdp_model.pth       # PyTorch LSTM Model weights
│   ├── scaler.pkl          # Feature scaling parameters
│   └── anomaly_model.pkl   # Isolation Forest model
├── scripts/                # Utility scripts for preprocessing and training
├── tests/                  # Pytest suite (Unit and Integration tests)
└── requirements.txt        # Python dependency list
```

---

## ⚙️ Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/FIABS.git
cd FIABS
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage Instructions

### 1. Start the Backend API
The FastAPI server handles all ML processing and authentication.
```bash
python ml_api/app.py
# Server runs at http://127.0.0.1:8001
```

### 2. Serve the Frontend
You can use any static file server. For example:
```bash
python -m http.server 5500
# Access the UI at http://127.0.0.1:5500/frontend/login.html
```

### 3. Demo Credentials
| Role | Username | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin` | `policy123` |
| **Financial Analyst** | `analyst` | `analyst123` |
| **Public Viewer** | `public` | `public123` |

---

## 🧠 Model Training & Testing

### Training the GDP Forecast Model
To retrain the LSTM model on the latest fiscal data:
```bash
python scripts/train_model.py
```

### Evaluating Performance
Run the evaluation script to generate MAE/RMSE metrics and trend graphs:
```bash
python scripts/evaluate_gdp_model.py
```
*Outputs are saved in the `outputs/` folder.*

---

## 🧪 Testing & Validation

FIABS includes a robust test suite covering auth, logic, and API endpoints.

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Generate Coverage Report
```bash
python -m pytest --cov=ml_api tests/ --cov-report=html
```

---

## 📊 Results & Outputs

- **Accuracy**: The LSTM model currently achieves high precision in recursive GDP forecasting with distinct visual cues for predicted vs. historical data.
- **Risk Analysis**: Integrated Monte Carlo simulations provide Min/Max/Avg GDP outlooks based on inflation variance.
- **Visuals**: Real-time charts powered by Chart.js visualize anomalies and allocation scores.

---

## 🤝 Contributing Guidelines

1.  **Fork** the repository.
2.  Create a **Feature Branch** (`git checkout -b feature/NewInsight`).
3.  Ensure code follows **PEP 8** standards.
4.  Run **Pytest** before submitting.
5.  Open a **Pull Request** with a detailed description of changes.

---

## 📄 License
This project is licensed under the **MIT License** - see the LICENSE file for details.

---

## 🙏 Acknowledgements
- **Frameworks**: FastAPI, PyTorch, Scikit-Learn.
- **UI/UX**: Inter Font, Chart.js.
- **Inspiration**: Recursive Multi-year Forecasting models and MCDM Decision Science.
