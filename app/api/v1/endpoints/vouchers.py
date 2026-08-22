from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models import Voucher
from app.schemas.voucher import VoucherCreate, VoucherResponse
from app.services.ledger_service import LedgerService

router = APIRouter()

@router.get("/", response_model=List[VoucherResponse])
def list_vouchers(db: Session = Depends(get_db)):
    vouchers = db.query(Voucher).order_by(Voucher.id.desc()).all()
    return vouchers

@router.post("/", response_model=VoucherResponse)
def create_voucher(data: VoucherCreate, db: Session = Depends(get_db)):
    return LedgerService.create_voucher(db, data)

@router.post("/{voucher_id}/review", response_model=VoucherResponse)
def review_voucher(voucher_id: int, reviewer: str = "supervisor", db: Session = Depends(get_db)):
    return LedgerService.review_voucher(db, voucher_id, reviewer)

@router.post("/{voucher_id}/post", response_model=VoucherResponse)
def post_voucher(voucher_id: int, poster: str = "controller", db: Session = Depends(get_db)):
    return LedgerService.post_voucher(db, voucher_id, poster)