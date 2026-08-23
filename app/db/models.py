import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.orm import relationship
import enum
from app.db.session import Base

class AccountCategory(str, enum.Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"

class NormalBalance(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class VoucherType(str, enum.Enum):
    JV = "JV"   # Journal Voucher
    PV = "PV"   # Payment Voucher (سند صرف)
    RV = "RV"   # Receipt Voucher (سند قبض)

class VoucherStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    POSTED = "POSTED"
    REJECTED = "REJECTED"

class Account(Base):
    __tablename__ = "accounts"

    code = Column(String(20), primary_key=True, index=True)
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    category = Column(SQLEnum(AccountCategory), nullable=False)
    normal_balance = Column(SQLEnum(NormalBalance), nullable=False)
    parent_code = Column(String(20), ForeignKey("accounts.code"), nullable=True)
    is_active = Column(Boolean, default=True)

    parent = relationship("Account", remote_side=[code], backref="children")

class Voucher(Base):
    __tablename__ = "vouchers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    voucher_no = Column(String(50), unique=True, index=True, nullable=False)
    voucher_type = Column(SQLEnum(VoucherType), nullable=False, default=VoucherType.JV)
    status = Column(SQLEnum(VoucherStatus), nullable=False, default=VoucherStatus.DRAFT)
    currency = Column(String(10), default="USD")
    exchange_rate = Column(Float, default=1.0)
    cost_center = Column(String(50), default="HQ-MAIN")
    memo = Column(Text, nullable=False)
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    reviewed_at = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(50), nullable=True)
    posted_by = Column(String(50), nullable=True)

    lines = relationship("VoucherLine", back_populates="voucher", cascade="all, delete-orphan")

class VoucherLine(Base):
    __tablename__ = "voucher_lines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    voucher_id = Column(Integer, ForeignKey("vouchers.id"), nullable=False)
    account_code = Column(String(20), ForeignKey("accounts.code"), nullable=False)
    debit_amount = Column(Float, default=0.0)
    credit_amount = Column(Float, default=0.0)
    line_memo = Column(String(255), nullable=True)

    voucher = relationship("Voucher", back_populates="lines")
    account = relationship("Account")

class GeneralLedgerEntry(Base):
    __tablename__ = "general_ledger"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    voucher_id = Column(Integer, ForeignKey("vouchers.id"), nullable=False)
    voucher_no = Column(String(50), index=True, nullable=False)
    entry_date = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    account_code = Column(String(20), ForeignKey("accounts.code"), nullable=False)
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    base_debit = Column(Float, default=0.0)
    base_credit = Column(Float, default=0.0)
    cost_center = Column(String(50), default="HQ-MAIN")
    memo = Column(Text, nullable=False)

    account = relationship("Account")
    voucher = relationship("Voucher")

def seed_chart_of_accounts(db):
    if db.query(Account).first():
        return

    sample_accounts = [
        # Assets
        Account(code="1000", name_en="Assets", name_ar="الأصول", category=AccountCategory.ASSET, normal_balance=NormalBalance.DEBIT, parent_code=None),
        Account(code="1010", name_en="Cash on Hand (Vault)", name_ar="الصندوق الرئيسي", category=AccountCategory.ASSET, normal_balance=NormalBalance.DEBIT, parent_code="1000"),
        Account(code="1020", name_en="Commercial Bank Account (USD)", name_ar="البنك التجاري (دولار)", category=AccountCategory.ASSET, normal_balance=NormalBalance.DEBIT, parent_code="1000"),
        Account(code="1050", name_en="Financing & Loans Portfolio", name_ar="محفظة التمويلات والقروض", category=AccountCategory.ASSET, normal_balance=NormalBalance.DEBIT, parent_code="1000"),
        
        # Liabilities
        Account(code="2000", name_en="Liabilities", name_ar="الخصوم والالتزامات", category=AccountCategory.LIABILITY, normal_balance=NormalBalance.CREDIT, parent_code=None),
        Account(code="2010", name_en="Suppliers & Vendor Payables", name_ar="حسابات الموردين والدائنين", category=AccountCategory.LIABILITY, normal_balance=NormalBalance.CREDIT, parent_code="2000"),
        Account(code="2020", name_en="Customer Security Deposits", name_ar="تأمينات وضمانات العملاء", category=AccountCategory.LIABILITY, normal_balance=NormalBalance.CREDIT, parent_code="2000"),
        
        # Equity
        Account(code="3000", name_en="Equity", name_ar="حقوق الملكية", category=AccountCategory.EQUITY, normal_balance=NormalBalance.CREDIT, parent_code=None),
        Account(code="3010", name_en="Paid-in Share Capital", name_ar="رأس المال المدفوع", category=AccountCategory.EQUITY, normal_balance=NormalBalance.CREDIT, parent_code="3000"),
        Account(code="3020", name_en="Retained Earnings", name_ar="الأرباح المبقاة والمحتجزة", category=AccountCategory.EQUITY, normal_balance=NormalBalance.CREDIT, parent_code="3000"),
        
        # Revenue
        Account(code="4000", name_en="Revenues", name_ar="الإيرادات", category=AccountCategory.REVENUE, normal_balance=NormalBalance.CREDIT, parent_code=None),
        Account(code="4010", name_en="Financing Return & Murabaha Revenue", name_ar="عوائد التمويل والمرابحة", category=AccountCategory.REVENUE, normal_balance=NormalBalance.CREDIT, parent_code="4000"),
        Account(code="4201", name_en="Unrealized FX Gain/Loss", name_ar="فروق تقييم العملات الأجنبية", category=AccountCategory.REVENUE, normal_balance=NormalBalance.CREDIT, parent_code="4000"),
        
        # Expenses
        Account(code="5000", name_en="Expenses", name_ar="المصروفات", category=AccountCategory.EXPENSE, normal_balance=NormalBalance.DEBIT, parent_code=None),
        Account(code="5010", name_en="General & Administrative Expenses", name_ar="المصروفات الإدارية والعمومية", category=AccountCategory.EXPENSE, normal_balance=NormalBalance.DEBIT, parent_code="5000"),
        Account(code="5020", name_en="Loan Loss Provisioning", name_ar="مخصص خسائر الائتمان والتمويل", category=AccountCategory.EXPENSE, normal_balance=NormalBalance.DEBIT, parent_code="5000")
    ]

    for acc in sample_accounts:
        db.add(acc)
    db.commit()