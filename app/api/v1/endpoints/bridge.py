from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models import VoucherType
from app.schemas.voucher import VoucherCreate, VoucherLineCreate
from app.services.ledger_service import LedgerService

router = APIRouter()

class LoanDisbursementRequest(BaseModel):
    loan_contract_id: str
    customer_name: str
    amount: float
    currency: str = "USD"
    bank_account_code: str = "1020"
    loan_portfolio_code: str = "1050"

@router.post("/loan-disbursement")
def bridge_loan_disbursement(req: LoanDisbursementRequest, db: Session = Depends(get_db)):
    memo = f"Automated Loan Disbursement for {req.customer_name} (Contract: {req.loan_contract_id})"
    voucher_data = VoucherCreate(
        voucher_type=VoucherType.PV,
        currency=req.currency,
        exchange_rate=1.0,
        cost_center="CREDIT-DEPT",
        memo=memo,
        lines=[
            VoucherLineCreate(account_code=req.loan_portfolio_code, debit_amount=req.amount, credit_amount=0.0, line_memo=f"Debit Loan Portfolio: {req.customer_name}"),
            VoucherLineCreate(account_code=req.bank_account_code, debit_amount=0.0, credit_amount=req.amount, line_memo="Credit Bank Account (Disbursement)")
        ]
    )
    v = LedgerService.create_voucher(db, voucher_data)
    v_reviewed = LedgerService.review_voucher(db, v.id, reviewer="auto_bridge_engine")
    v_posted = LedgerService.post_voucher(db, v_reviewed.id, poster="auto_posting_service")
    return {
        "status": "success",
        "message": "Loan disbursement posted to General Ledger automatically.",
        "voucher_no": v_posted.voucher_no,
        "posted_at": v_posted.posted_at
    }