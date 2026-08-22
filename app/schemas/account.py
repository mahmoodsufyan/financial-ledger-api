from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.db.models import AccountCategory, NormalBalance

class AccountBase(BaseModel):
    code: str
    name_en: str
    name_ar: str
    category: AccountCategory
    normal_balance: NormalBalance
    parent_code: Optional[str] = None
    is_active: bool = True

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    balance: float = 0.0
    model_config = ConfigDict(from_attributes=True)

class AccountTreeItem(AccountResponse):
    children: List['AccountTreeItem'] = []