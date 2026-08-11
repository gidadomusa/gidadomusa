## Hi there 👋

-->



explainable-ai-financial-risk-platform/
│
├── README.md
├── requirements.txt
├── docker-compose.yml
├── .gitignore
│
├── data/
│   ├── raw/
│   │   └── creditcard.csv
│   │
│   ├── processed/
│   │   └── cleaned_data.csv
│   │
│   └── sample_inputs/
│       └── transactions.json
│
├── notebooks/
│   ├── 01_EDA.ipynb
│   ├── 02_Feature_Engineering.ipynb
│   ├── 03_Model_Training.ipynb
│   └── 04_SHAP_Analysis.ipynb
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   └── routes.py
│   │   │
│   │   ├── models/
│   │   │   ├── predictor.py
│   │   │   ├── train.py
│   │   │   └── shap_engine.py
│   │   │
│   │   ├── database/
│   │   │   ├── db.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── utils/
│   │   │   ├── preprocess.py
│   │   │   ├── metrics.py
│   │   │   └── logger.py
│   │   │
│   │   └── config.py
│   │
│   ├── trained_models/
│   │   ├── xgboost_model.pkl
│   │   ├── random_forest_model.pkl
│   │   └── shap_explainer.pkl
│   │
│   ├── tests/
│   │   └── test_prediction.py
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   │
│   ├── public/
│   │
│   ├── src/
│   │   │
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── RiskCard.jsx
│   │   │   ├── SHAPChart.jsx
│   │   │   ├── PredictionForm.jsx
│   │   │   ├── MetricsPanel.jsx
│   │   │   └── AuditTable.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── PredictionPage.jsx
│   │   │   ├── AuditLogs.jsx
│   │   │   └── ModelMonitoring.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── hooks/
│   │   │   └── usePrediction.js
│   │   │
│   │   ├── assets/
│   │   │
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   └── Dockerfile
│
├── visualizations/
│   ├── shap_summary.png
│   ├── shap_force_plot.png
│   ├── feature_importance.png
│   └── confusion_matrix.png
│
├── docs/
│   ├── architecture.png
│   ├── system_design.md
│   ├── api_documentation.md
│   └── deployment_guide.md
│
└── deployment/
    ├── vercel.json
    ├── render.yaml
    └── nginx.conf