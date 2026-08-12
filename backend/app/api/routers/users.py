from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from backend.app.db import get_session
from backend.app.models.user import User, UserRead

router = APIRouter()

@router.get("/{user_id}", response_model=UserRead, tags=["users"])
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
