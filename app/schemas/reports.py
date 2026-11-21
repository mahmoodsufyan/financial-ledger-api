from pydantic import BaseModel
from decimal import Decimal
from typing import List

class TrialBalanceItem(BaseModel):
    account_code: str
    account_name_en: str
    account_name_ar: str
    category: str
    debit: Decimal
    credit: Decimal

class TrialBalanceReport(BaseModel):
    base_currency: str
    total_debit: Decimal
    total_credit: Decimal
    is_balanced: bool
    items: List[TrialBalanceItem]

class IncomeStatementReport(BaseModel):
    total_revenues: Decimal
    total_expenses: Decimal
    net_income: Decimal
    revenue_items: List[TrialBalanceItem]
    expense_items: List[TrialBalanceItem]