from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import List, Optional
import datetime
from app.core.money import Money, ExchangeRate, Currency, ZERO
from app.db.models import VoucherType, VoucherStatus

class VoucherLineBase(BaseModel):
    account_code: str
    debit_amount: Money = ZERO
    credit_amount: Money = ZERO
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
    currency: Currency = "USD"
    exchange_rate: ExchangeRate = 1
    cost_center: str = "HQ-MAIN"
    memo: str
    lines: List[VoucherLineCreate] = Field(max_length=1000)

    @model_validator(mode='after')
    def check_double_entry_balance(self):
        if len(self.lines) < 2:
            raise ValueError("A double-entry voucher must contain at least 2 line items.")
        
        for line in self.lines:
            if (line.debit_amount > 0) == (line.credit_amount > 0):
                raise ValueError("Each line must have exactly one positive debit or credit.")

        sum_debit = sum(line.debit_amount for line in self.lines)
        sum_credit = sum(line.credit_amount for line in self.lines)

        if sum_debit >= 10**12:
            raise ValueError("Demo voucher total must be below 1 trillion currency units.")
        
        if sum_debit != sum_credit:
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
    exchange_rate: ExchangeRate
    cost_center: str
    memo: str
    total_amount: Money
    created_at: datetime.datetime
    reviewed_at: Optional[datetime.datetime] = None
    posted_at: Optional[datetime.datetime] = None
    lines: List[VoucherLineResponse] = []
    model_config = ConfigDict(from_attributes=True)
