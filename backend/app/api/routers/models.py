from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from backend.app.models.loader import scan_models, load_model, predict_pytorch

router = APIRouter()

class PredictPayload(BaseModel):
    input: Any

@router.get("/", tags=["models"])
def list_models():
    return scan_models()

@router.post("/{name}/predict", tags=["models"]) 
def predict(name: str, payload: PredictPayload):
    try:
        return predict_pytorch(name, payload.input)
    except KeyError:
        raise HTTPException(status_code=404, detail="Model not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
