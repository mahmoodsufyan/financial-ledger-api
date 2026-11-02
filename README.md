# 🏛️ Enterprise Multi-Currency Financial Ledger & Accounting API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python)](https://python.org)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-red.svg)](https://sqlalchemy.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2.6-green.svg)](https://docs.pydantic.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker)](Dockerfile)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A public portfolio demonstration of a high-precision **Double-Entry Financial Accounting and General Ledger Engine** built with Python and FastAPI. Implements rigorous double-entry balancing rules ($\\sum \\text{Debit} == \\sum \\text{Credit}$), a 3-tier voucher state machine (`Draft` ➔ `Reviewed` ➔ `Posted`), hierarchical chart of accounts, real-time trial balance reporting, and automated posting bridges for loan disbursements and remittances.

---

## Implementation context

This repository contains a Python/FastAPI portfolio demo. The [Oracle implementation case study](docs/CASE_STUDY.md) describes related Oracle APEX, PL/SQL, and ORDS work. This demo is a separate implementation and does not contain the original enterprise application.

## 🚀 Key Features

* **Strict Double-Entry Enforcement:** Programmatic guarantees preventing unbalanced voucher creation at the Pydantic and database levels.
* **3-Stage Transaction Lifecycle:** `DRAFT` (Data Entry) ➔ `REVIEWED` (Supervisory Check) ➔ `POSTED` (Atomic Ledger Write).
* **Hierarchical Chart of Accounts:** Multi-level parent-child tree mapping assets, liabilities, equity, revenues, and expenses with normal balance classifications.
* **Automated Operational Bridges:** Direct endpoints generating balanced atomic journal entries from external credit/loan disbursements and supplier remittances.
* **Real-Time Financial Intelligence:** Instant on-demand generation of consolidated **Trial Balances** and ledger summaries.
* **Interactive Web Dashboard:** Built-in responsive UI with double-entry simulator, chart of accounts explorer, and financial breakdown charts.

---

## 🛠️ Quick Start

### 1. Local Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8000
```

* **Interactive Web Dashboard:** [http://localhost:8000/](http://localhost:8000/)
* **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 2. Run with Docker
```bash
docker-compose up --build
```

### 3. Run Automated Test Suite
```bash
pytest
```

---

## 📖 Full Engineering Case Study
Read the background and architecture of the related Oracle implementation:
* 📄 **[Enterprise Case Study: Multi-Currency General Ledger System](docs/CASE_STUDY.md)**