import json
from typing import Any, Dict
from domain import create_item, list_items

def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        },
        "body": json.dumps(body),
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method = event["requestContext"]["http"]["method"]
    path   = event["requestContext"]["http"]["path"]

    # Opcional si no usas CORS de API Gateway
    if method == "OPTIONS":
        return _response(200, {"ok": True})

    if path == "/dev/health" and method == "GET":
        return _response(200, {"status": "ok"})

    if path == "/dev/items" and method == "GET":
        items = [
            {"id": i.id, "name": i.name, "price": i.price}
            for i in list_items()
        ]
        return _response(200, {"items": items})

    if path == "/dev/items" and method == "POST":
        try:
            body = json.loads(event.get("body") or "{}")
            item = create_item(body["name"], body["price"])
            return _response(201, {
                "id": item.id, 
                "name": item.name, 
                "price": item.price
            })
        except Exception as exc:
            return _response(400, {"error": str(exc)})

    return _response(404, {"error": "not found"})
