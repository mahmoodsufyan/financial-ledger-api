from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.models import GeneralLedgerEntry
from app.db.session import SessionLocal

client = TestClient(app)

def payload(debit='1.00', credit='1.00'):
    return {
        'memo': 'Synthetic precision regression',
        'lines': [
            {'account_code': '1010', 'debit_amount': debit},
            {'account_code': '1020', 'credit_amount': credit},
        ],
    }

@pytest.mark.parametrize('amount', ['1.004', 'NaN', 'Infinity', '-1.00'])
def test_reject_invalid_amounts(amount):
    assert client.post('/api/v1/vouchers/', json=payload(amount)).status_code == 422

def test_reject_unsupported_currency():
    data = payload()
    data['currency'] = 'JPY'
    assert client.post('/api/v1/vouchers/', json=data).status_code == 422

def test_reject_bridge_subcent_amount():
    data = {'loan_contract_id': 'demo', 'customer_name': 'Synthetic', 'amount': '1.004'}
    assert client.post('/api/v1/bridge/loan-disbursement', json=data).status_code == 422

def test_decimal_round_trip_and_no_repeat_post():
    response = client.post('/api/v1/vouchers/', json=payload('0.30', '0.30'))
    assert response.status_code == 200, response.text
    voucher = response.json()
    assert Decimal(str(voucher['total_amount'])) == Decimal('0.30')
    assert Decimal(str(voucher['lines'][0]['debit_amount'])) == Decimal('0.30')
    voucher_id = voucher['id']
    assert client.post(f'/api/v1/vouchers/{voucher_id}/review').status_code == 200
    assert client.post(f'/api/v1/vouchers/{voucher_id}/post').status_code == 200
    assert client.post(f'/api/v1/vouchers/{voucher_id}/post').status_code == 400
    with SessionLocal() as db:
        rows = db.query(GeneralLedgerEntry).filter_by(voucher_id=voucher_id).all()
        assert len(rows) == 2
        assert sum(row.debit for row in rows) == Decimal('0.30')

def test_conversion_keeps_split_journal_balanced():
    data = payload()
    data['currency'] = 'EUR'
    data['exchange_rate'] = '0.5'
    data['lines'] = [
        {'account_code': '1010', 'debit_amount': '1.01'},
        {'account_code': '1050', 'debit_amount': '1.01'},
        {'account_code': '1020', 'credit_amount': '2.02'},
    ]
    response = client.post('/api/v1/vouchers/', json=data)
    assert response.status_code == 200, response.text
    voucher_id = response.json()['id']
    assert client.post(f'/api/v1/vouchers/{voucher_id}/review').status_code == 200
    assert client.post(f'/api/v1/vouchers/{voucher_id}/post').status_code == 200
    with SessionLocal() as db:
        rows = db.query(GeneralLedgerEntry).filter_by(voucher_id=voucher_id).all()
        assert sum(row.base_debit for row in rows) == Decimal('1.01')
        assert sum(row.base_credit for row in rows) == Decimal('1.01')

def test_concurrent_creation_uses_database_allocated_numbers():
    def create(_):
        with TestClient(app) as local_client:
            response = local_client.post('/api/v1/vouchers/', json=payload('12.34', '12.34'))
            assert response.status_code == 200, response.text
            return response.json()

    with ThreadPoolExecutor(max_workers=8) as executor:
        vouchers = list(executor.map(create, range(24)))
    assert len({v['voucher_no'] for v in vouchers}) == 24
    for voucher in vouchers:
        assert voucher['voucher_no'].endswith(f"-{voucher['id']:08d}")
