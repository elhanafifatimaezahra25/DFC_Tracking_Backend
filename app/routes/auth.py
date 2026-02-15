from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ..models.user import User
from ..schemas.user import UserCreate, UserRead
from ..core import security
from .. import database

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user_in: UserCreate, session: Session = Depends(database.get_session)):
    exists = session.exec(select(User).where(User.email == user_in.email)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = security.get_password_hash(user_in.password)
    new_user = User(
        matricule=user_in.matricule,
        last_name=user_in.last_name,
        first_name=user_in.first_name,
        email=user_in.email,
        role=user_in.role,
        hashed_password=hashed,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    token = security.create_access_token(str(new_user.id))
    return {
        "access_token": token,
        "user": {
            "id": new_user.id,
            "matricule": new_user.matricule,
            "email": new_user.email,
            "role": new_user.role,
        }
    }

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(database.get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    token = security.create_access_token(str(user.id))
    return {"access_token": token}

@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(security.get_current_user)):
    return current_user
