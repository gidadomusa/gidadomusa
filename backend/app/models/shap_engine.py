def explain_prediction(features: dict) -> list[dict]:
    return [{"feature": key, "impact": value} for key, value in features.items()]
