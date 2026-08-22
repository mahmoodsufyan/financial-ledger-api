from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.reports import TrialBalanceReport
from app.services.ledger_service import LedgerService

router = APIRouter()

@router.get("/trial-balance", response_model=TrialBalanceReport)
def get_trial_balance(db: Session = Depends(get_db)):
    return LedgerService.get_trial_balance(db)