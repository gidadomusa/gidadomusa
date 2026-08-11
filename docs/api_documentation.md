# API Documentation

`GET /health` returns service status.

`POST /api/predict` accepts `amount`, `hour`, `distance_from_home_km`, and `recent_transaction_count`, returning a risk score, label, and feature impacts.
