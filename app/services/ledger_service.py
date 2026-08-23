import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models import (
    Voucher, VoucherLine, GeneralLedgerEntry, VoucherStatus, 
    Account, NormalBalance, AccountCategory
)
from app.schemas.voucher import VoucherCreate

class LedgerService:
    @staticmethod
    def create_voucher(db: Session, data: VoucherCreate, user: str = "system") -> Voucher:
        total_amount = sum(l.debit_amount for l in data.lines)
        v_count = db.query(Voucher).count() + 1
        voucher_no = f"{data.voucher_type.value}-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m')}-{v_count:04d}"

        voucher = Voucher(
            voucher_no=voucher_no,
            voucher_type=data.voucher_type,
            status=VoucherStatus.DRAFT,
            currency=data.currency,
            exchange_rate=data.exchange_rate,
            cost_center=data.cost_center,
            memo=data.memo,
            total_amount=total_amount
        )
        db.add(voucher)
        db.flush()

        for line in data.lines:
            # verify account exists
            acc = db.query(Account).filter(Account.code == line.account_code).first()
            if not acc:
                raise HTTPException(status_code=400, detail=f"Account {line.account_code} does not exist.")
            
            v_line = VoucherLine(
                voucher_id=voucher.id,
                account_code=line.account_code,
                debit_amount=line.debit_amount,
                credit_amount=line.credit_amount,
                line_memo=line.line_memo
            )
            db.add(v_line)

        db.commit()
        db.refresh(voucher)
        return voucher

    @staticmethod
    def review_voucher(db: Session, voucher_id: int, reviewer: str = "supervisor") -> Voucher:
        voucher = db.query(Voucher).filter(Voucher.id == voucher_id).with_for_update().first()
        if not voucher:
            raise HTTPException(status_code=404, detail="Voucher not found.")
        
        if voucher.status != VoucherStatus.DRAFT:
            raise HTTPException(status_code=400, detail=f"Only DRAFT vouchers can be reviewed. Current: {voucher.status.value}")
        
        voucher.status = VoucherStatus.REVIEWED
        voucher.reviewed_at = datetime.datetime.now(datetime.timezone.utc)
        voucher.reviewed_by = reviewer
        db.commit()
        db.refresh(voucher)
        return voucher

    @staticmethod
    def post_voucher(db: Session, voucher_id: int, poster: str = "controller") -> Voucher:
        voucher = db.query(Voucher).filter(Voucher.id == voucher_id).with_for_update().first()
        if not voucher:
            raise HTTPException(status_code=404, detail="Voucher not found.")
        
        if voucher.status != VoucherStatus.REVIEWED:
            raise HTTPException(status_code=400, detail=f"Only REVIEWED vouchers can be posted. Current: {voucher.status.value}")
        
        # Verify double entry balance
        sum_debit = sum(l.debit_amount for l in voucher.lines)
        sum_credit = sum(l.credit_amount for l in voucher.lines)
        if round(sum_debit, 2) != round(sum_credit, 2) or sum_debit <= 0:
            raise HTTPException(status_code=400, detail="Voucher legs are out of balance.")

        # Atomic insert into General Ledger
        for line in voucher.lines:
            gl_entry = GeneralLedgerEntry(
                voucher_id=voucher.id,
                voucher_no=voucher.voucher_no,
                entry_date=datetime.datetime.now(datetime.timezone.utc),
                account_code=line.account_code,
                debit=line.debit_amount,
                credit=line.credit_amount,
                currency=voucher.currency,
                base_debit=line.debit_amount * voucher.exchange_rate,
                base_credit=line.credit_amount * voucher.exchange_rate,
                cost_center=voucher.cost_center,
                memo=line.line_memo or voucher.memo
            )
            db.add(gl_entry)

        voucher.status = VoucherStatus.POSTED
        voucher.posted_at = datetime.datetime.now(datetime.timezone.utc)
        voucher.posted_by = poster
        db.commit()
        db.refresh(voucher)
        return voucher

    @staticmethod
    def get_trial_balance(db: Session):
        accounts = db.query(Account).all()
        items = []
        total_debit = 0.0
        total_credit = 0.0

        for acc in accounts:
            # sum all GL entries
            gl_entries = db.query(GeneralLedgerEntry).filter(GeneralLedgerEntry.account_code == acc.code).all()
            sum_d = sum(e.base_debit for e in gl_entries)
            sum_c = sum(e.base_credit for e in gl_entries)

            net = sum_d - sum_c
            debit_val = 0.0
            credit_val = 0.0

            if acc.normal_balance == NormalBalance.DEBIT:
                if net >= 0:
                    debit_val = net
                else:
                    credit_val = abs(net)
            else:
                if net <= 0:
                    credit_val = abs(net)
                else:
                    debit_val = net

            if debit_val > 0 or credit_val > 0:
                items.append({
                    "account_code": acc.code,
                    "account_name_en": acc.name_en,
                    "account_name_ar": acc.name_ar,
                    "category": acc.category.value,
                    "debit": round(debit_val, 2),
                    "credit": round(credit_val, 2)
                })
                total_debit += debit_val
                total_credit += credit_val

        return {
            "base_currency": "USD",
            "total_debit": round(total_debit, 2),
            "total_credit": round(total_credit, 2),
            "is_balanced": round(total_debit, 2) == round(total_credit, 2),
            "items": items
        }