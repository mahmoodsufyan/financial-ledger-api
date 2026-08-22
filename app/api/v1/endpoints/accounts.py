from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models import Account
from app.schemas.account import AccountResponse, AccountCreate

router = APIRouter()

@router.get("/", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return accounts

@router.post("/", response_model=AccountResponse)
def create_account(data: AccountCreate, db: Session = Depends(get_db)):
    existing = db.query(Account).filter(Account.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account code already exists.")
    
    acc = Account(**data.dict())
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc