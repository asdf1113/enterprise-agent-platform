from tools.business_data import get_product_info


class FakeDatabase:
    def get_product_info(self, product_name: str):
        if product_name != "X200":
            return None

        return {
            "product_id": 2,
            "product_name": "X200",
            "category": "Industrial Controller",
            "unit_price": 6999.00,
            "description": "Test product",
            "active": True,
        }


def test_get_product_info_found() -> None:
    result = get_product_info(FakeDatabase(), "X200")

    assert result["found"] is True
    assert result["product"]["product_name"] == "X200"


def test_get_product_info_not_found() -> None:
    result = get_product_info(FakeDatabase(), "UNKNOWN")

    assert result == {
        "found": False,
        "product_name": "UNKNOWN",
    }
