# tests/test_transaction_service.py

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session
from app.services.transaction_service import initialize_user_transaction, handle_transaction_webhook
from app.models.transaction import Transaction

@pytest.mark.asyncio
async def test_initialize_user_transaction_success(mocker):
    # Mock the initialize_transaction Paystack utility
    mock_response = {
        "authorization_url": "https://paystack.com/pay/transaction",
        "access_code": "ACCESS123",
        "reference": "REF1234567890"
    }
    mocker.patch('app.utils.paystack_utils.initialize_transaction', return_value=mock_response)

    # Mock the database session
    mock_db = AsyncMock(spec=Session)
    mock_db.add = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    result = await initialize_user_transaction(
        db=mock_db,
        email="test@example.com",
        amount=1000.0,
        channel="card",
        additional_data=None,
        metadata={"order_id": "ORDER123"}
    )

    assert result["authorization_url"] == mock_response["authorization_url"]
    assert result["access_code"] == mock_response["access_code"]
    assert result["reference"] == mock_response["reference"]
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
