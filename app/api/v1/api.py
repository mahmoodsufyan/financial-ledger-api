from fastapi import APIRouter
from app.api.v1.endpoints import accounts, vouchers, reports, bridge

api_router = APIRouter()
api_router.include_router(accounts.router, prefix="/accounts", tags=["Chart of Accounts"])
api_router.include_router(vouchers.router, prefix="/vouchers", tags=["Vouchers & Posting"])
api_router.include_router(reports.router, prefix="/reports", tags=["Financial Reports"])
api_router.include_router(bridge.router, prefix="/bridge", tags=["Automated Posting Bridge"])