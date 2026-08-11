def predict_risk(transaction: dict) -> dict:
    contributions = {
        "amount": min(transaction["amount"] / 1000, 1.0),
        "hour": 0.2 if transaction["hour"] < 5 else 0.0,
        "distance_from_home_km": min(transaction["distance_from_home_km"] / 500, 1.0),
        "recent_transaction_count": min(transaction["recent_transaction_count"] / 20, 1.0),
    }
    score = min(sum(contributions.values()) / 3, 1.0)
    return {
        "risk_score": round(score, 4),
        "risk_label": "high" if score >= 0.5 else "low",
        "explanations": [
            {"feature": feature, "impact": round(value, 4)}
            for feature, value in sorted(
                contributions.items(), key=lambda item: item[1], reverse=True
            )
        ],
    }