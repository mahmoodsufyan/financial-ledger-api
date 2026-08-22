import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_chart_of_accounts():
    response = client.get("/api/v1/accounts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 8
    codes = [a["code"] for a in data]
    assert "1010" in codes
    assert "1020" in codes
    assert "1050" in codes

def test_create_and_post_voucher_lifecycle():
    # 1. Create balanced voucher
    voucher_payload = {
        "voucher_type": "JV",
        "currency": "USD",
        "exchange_rate": 1.0,
        "cost_center": "HQ-MAIN",
        "memo": "Test automated capital transfer voucher",
        "lines": [
            {"account_code": "1010", "debit_amount": 5000.0, "credit_amount": 0.0, "line_memo": "Debit Cash"},
            {"account_code": "1020", "debit_amount": 0.0, "credit_amount": 5000.0, "line_memo": "Credit Bank"}
        ]
    }
    create_res = client.post("/api/v1/vouchers/", json=voucher_payload)
    assert create_res.status_code == 200
    v_data = create_res.json()
    assert v_data["status"] == "DRAFT"
    voucher_id = v_data["id"]

    # 2. Review voucher
    review_res = client.post(f"/api/v1/vouchers/{voucher_id}/review")
    assert review_res.status_code == 200
    assert review_res.json()["status"] == "REVIEWED"

    # 3. Post voucher atomically
    post_res = client.post(f"/api/v1/vouchers/{voucher_id}/post")
    assert post_res.status_code == 200
    assert post_res.json()["status"] == "POSTED"

def test_prevent_unbalanced_voucher():
    unbalanced_payload = {
        "voucher_type": "JV",
        "currency": "USD",
        "exchange_rate": 1.0,
        "cost_center": "HQ-MAIN",
        "memo": "Out of balance attempt",
        "lines": [
            {"account_code": "1010", "debit_amount": 5000.0, "credit_amount": 0.0},
            {"account_code": "1020", "debit_amount": 0.0, "credit_amount": 4000.0}
        ]
    }
    response = client.post("/api/v1/vouchers/", json=unbalanced_payload)
    assert response.status_code == 422  # Pydantic validation error

def test_trial_balance_generation():
    response = client.get("/api/v1/reports/trial-balance")
    assert response.status_code == 200
    tb = response.json()
    assert tb["is_balanced"] is True
    assert tb["total_debit"] == tb["total_credit"]

def test_automated_loan_bridge():
    bridge_payload = {
        "loan_contract_id": "LN-TEST-101",
        "customer_name": "Al-Naseem Commercial Co.",
        "amount": 15000.0,
        "currency": "USD"
    }
    response = client.post("/api/v1/bridge/loan-disbursement", json=bridge_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "voucher_no" in data