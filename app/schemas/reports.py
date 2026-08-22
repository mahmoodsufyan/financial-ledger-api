from pydantic import BaseModel
from typing import List

class TrialBalanceItem(BaseModel):
    account_code: str
    account_name_en: str
    account_name_ar: str
    category: str
    debit: float
    credit: float

class TrialBalanceReport(BaseModel):
    base_currency: str
    total_debit: float
    total_credit: float
    is_balanced: bool
    items: List[TrialBalanceItem]

class IncomeStatementReport(BaseModel):
    total_revenues: float
    total_expenses: float
    net_income: float
    revenue_items: List[TrialBalanceItem]
    expense_items: List[TrialBalanceItem]