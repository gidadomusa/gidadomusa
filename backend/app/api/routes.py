from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.predictor import predict_risk

router = APIRouter()


class Transaction(BaseModel):
    amount: float = Field(ge=0)
    hour: int = Field(ge=0, le=23)
    distance_from_home_km: float = Field(ge=0)
    recent_transaction_count: int = Field(ge=0)


@router.post("/predict")
def predict(transaction: Transaction) -> dict:
    return predict_risk(transaction.model_dump())