import sys
import os
import json
from unittest.mock import MagicMock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
from app import handler  # noqa: E402
sys.modules["boto3"] = MagicMock()

os.environ.setdefault("TABLE_NAME", "dummy-table")

_FAKE_DB = []


class FakeItem:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price


def fake_create_item(name: str, price: float):
    item = FakeItem(
        id=str(len(_FAKE_DB) + 1),
        name=name,
        price=price
    )
    _FAKE_DB.append(item)
    return item


def fake_list_items():
    return list(_FAKE_DB)


def fake_reset_items():
    _FAKE_DB.clear()


handler.create_item = fake_create_item
handler.list_items = fake_list_items


def test_health_ok():
    event = {
        "rawPath": "/dev/health",
        "requestContext": {
            "http": {"method": "GET", "path": "/dev/health"}
        },
    }
    resp = handler.lambda_handler(event, None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["status"] == "ok"


def test_create_item_and_list():
    fake_reset_items()

    create_event = {
        "rawPath": "/dev/items",
        "requestContext": {"http": {"method": "POST", "path": "/dev/items"}},
        "body": json.dumps({"name": "Café", "price": 10.5}),
    }

    resp = handler.lambda_handler(create_event, None)
    assert resp["statusCode"] == 201
    created = json.loads(resp["body"])
    assert created["name"] == "Café"
    assert created["price"] == 10.5
    assert "id" in created

    list_event = {
        "rawPath": "/dev/items",
        "requestContext": {"http": {"method": "GET", "path": "/dev/items"}},
    }

    resp_list = handler.lambda_handler(list_event, None)
    assert resp_list["statusCode"] == 200

    items_body = json.loads(resp_list["body"])
    assert len(items_body["items"]) == 1
