# ============================================================
# MOCK DE BOTO3 PARA EVITAR REGION Y CONEXIONES REALES
# ============================================================
import sys
from unittest.mock import MagicMock
sys.modules["boto3"] = MagicMock()

import os
import json

# Variable de entorno requerida para domain.py
os.environ.setdefault("TABLE_NAME", "dummy-table")

# Ahora sí se pueden importar tus módulos sin que boto3 explote
from app.domain import reset_items
from app.handler import lambda_handler


def test_health_ok():
    event = {
        "rawPath": "/health",
        "requestContext": {"http": {"method": "GET"}},
    }

    resp = lambda_handler(event, None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["status"] == "ok"


def test_create_item_and_list():
    reset_items()

    create_event = {
        "rawPath": "/items",
        "requestContext": {"http": {"method": "POST"}},
        "body": json.dumps({"name": "Café", "price": 10.5}),
    }

    resp = lambda_handler(create_event, None)
    assert resp["statusCode"] == 201
    created = json.loads(resp["body"])
    assert created["name"] == "Café"
    assert created["price"] == 10.5
    assert "id" in created

    list_event = {
        "rawPath": "/items",
        "requestContext": {"http": {"method": "GET"}},
    }

    resp_list = lambda_handler(list_event, None)
    assert resp_list["statusCode"] == 200
    items_body = json.loads(resp_list["body"])
    assert len(items_body["items"]) == 1
