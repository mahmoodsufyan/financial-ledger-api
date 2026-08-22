from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import List, Optional
import datetime
from app.db.models import VoucherType, VoucherStatus

class VoucherLineBase(BaseModel):
    account_code: str
    debit_amount: float = Field(default=0.0, ge=0.0)
    credit_amount: float = Field(default=0.0, ge=0.0)
    line_memo: Optional[str] = None

class VoucherLineCreate(VoucherLineBase):
    pass

class VoucherLineResponse(VoucherLineBase):
    id: int
    account_name_en: Optional[str] = None
    account_name_ar: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class VoucherCreate(BaseModel):
    voucher_type: VoucherType = VoucherType.JV
    currency: str = "USD"
    exchange_rate: float = Field(default=1.0, gt=0.0)
    cost_center: str = "HQ-MAIN"
    memo: str
    lines: List[VoucherLineCreate]

    @model_validator(mode='after')
    def check_double_entry_balance(self):
        if len(self.lines) < 2:
            raise ValueError("A double-entry voucher must contain at least 2 line items.")
        
        sum_debit = sum(line.debit_amount for line in self.lines)
        sum_credit = sum(line.credit_amount for line in self.lines)
        
        if round(sum_debit, 2) != round(sum_credit, 2):
            raise ValueError(f"Out of balance: Total Debit ({sum_debit}) does not equal Total Credit ({sum_credit}).")
        
        if sum_debit <= 0:
            raise ValueError("Total voucher amount must be greater than zero.")
            
        return self

class VoucherResponse(BaseModel):
    id: int
    voucher_no: str
    voucher_type: VoucherType
    status: VoucherStatus
    currency: str
    exchange_rate: float
    cost_center: str
    memo: str
    total_amount: float
    created_at: datetime.datetime
    reviewed_at: Optional[datetime.datetime] = None
    posted_at: Optional[datetime.datetime] = None
    lines: List[VoucherLineResponse] = []
    model_config = ConfigDict(from_attributes=True)