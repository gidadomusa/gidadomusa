from pydantic import BaseModel


class AuditRecord(BaseModel):
    risk_score: float
    risk_label: str
