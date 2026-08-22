import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.api.v1.api import api_router
from app.db.session import init_db

# Initialize database schema and seeds
init_db()

app = FastAPI(
    title="🏛️ Enterprise Multi-Currency Financial & General Ledger API",
    description="""
## Enterprise Core Accounting & Ledger Engine
* **Double-Entry Balance Enforcer:** Strict programmatic guarantee $\\sum Debit == \\sum Credit$.
* **3-Tier Voucher Lifecycle:** Draft ➔ Review ➔ Atomic Posting.
* **Hierarchical Chart of Accounts:** Multi-level account trees with normal balance rules.
* **Automated Integration Bridge:** Instant journal creation for loan disbursements and vendor payouts.
* **Real-time Trial Balance & Financial Statements.**
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# Mount static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", tags=["Dashboard"], response_class=HTMLResponse)
def serve_root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Financial Ledger API Running</h1><p><a href='/docs'>Swagger Docs</a></p>")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Enterprise Financial Ledger API",
        "version": "1.0.0",
        "docs": "/docs"
    }