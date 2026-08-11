# Explainable AI Financial Risk Platform

An end-to-end prototype for reviewing financial transactions with a transparent risk assessment. The platform combines a FastAPI backend with a React/Vite frontend so risk teams can submit transaction details, inspect a risk score, and see which transaction signals contributed most to the result.

## What It Does

- Accepts transaction amount, hour of day, distance from home, and recent transaction count.
- Validates inputs through a typed FastAPI request model.
- Returns a normalized risk score and `low` or `high` risk label.
- Provides ranked feature contributions so each assessment is interpretable.
- Includes notebooks and model utilities for exploratory analysis, feature engineering, training, and SHAP analysis.
- Provides Docker Compose, Render, Vercel, and Nginx deployment configuration.

The current API uses a deterministic demo scorer in `backend/app/models/predictor.py`. The model-training and SHAP modules provide the foundation for replacing it with trained artifacts.

## Architecture

The system is split into two services:

- **Backend:** FastAPI service on port `8000`, exposing `/health` and `POST /api/predict`.
- **Frontend:** React/Vite application on port `5173`, providing the transaction review interface.

The repository also contains data placeholders, sample transaction input, analysis notebooks, tests, documentation, and deployment manifests.

## Quick Start

### Run with Docker Compose

```bash
docker compose up --build
```

Then open:

- Frontend: http://localhost:5173
- Backend health check: http://localhost:8000/health

### Run the services locally

Backend:

```bash
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Frontend, in a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

## API Example

```bash
curl -X POST http://localhost:8000/api/predict \
    -H "Content-Type: application/json" \
    -d '{
        "amount": 850,
        "hour": 2,
        "distance_from_home_km": 300,
        "recent_transaction_count": 8
    }'
```

The response includes `risk_score`, `risk_label`, and an `explanations` array sorted by feature impact. Full endpoint details are available in [API documentation](docs/api_documentation.md).

## Repository Layout

```text
backend/       FastAPI application, prediction logic, tests, and model artifacts
frontend/      React/Vite transaction review interface
data/          Raw, processed, and sample input data locations
notebooks/     EDA, feature engineering, training, and SHAP analysis notebooks
docs/          System design, API, and deployment documentation
deployment/    Render, Vercel, and Nginx configuration
```

## Project Status

This is an explainable-risk platform prototype. The scoring endpoint and review UI are available now; persistence, production model artifacts, and expanded monitoring workflows remain part of the platform's ongoing development.