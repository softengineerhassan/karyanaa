from decimal import Decimal

from app.core.response import error_response, success_response


def test_success_response_encodes_decimal_values() -> None:
    response = success_response(
        data={"price": Decimal("12.34"), "items": [Decimal("1.000")]},
        message="ok",
    )

    assert response["success"] is True
    assert response["data"]["price"] == 12.34
    assert response["data"]["items"] == [1.0]


def test_error_response_encodes_decimal_values() -> None:
    response = error_response(
        message="failed",
        details={"amount": Decimal("9.99")},
    )

    assert response["success"] is False
    assert response["details"]["amount"] == 9.99