import os
import uuid
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def _to_decimal(value):
    if isinstance(value, float):
        return Decimal(str(value))
    return value


def create_item(name: str, price: float) -> dict:
    item = {
        "id": str(uuid.uuid4()),
        "name": name,
        "price": _to_decimal(price),
    }
    table.put_item(Item=item)
    return item


def list_items() -> list[dict]:
    resp = table.scan()
    return resp.get("Items", [])

def reset_items() -> None:
    """
    Helper solo para tests:
    borra todos los items de la tabla (o del mock de boto3).
    """
    try:
        scan = table.scan()
        items = scan.get("Items", [])

        if not items:
            return

        with table.batch_writer() as batch:
            for item in items:
                # Ajusta la clave primaria según tu modelo
                batch.delete_item(Key={"id": item["id"]})
    except Exception:
        # En los tests con boto3 mockeado, esto no va a hacer nada real,
        # y cualquier error lo ignoramos porque solo es un helper.
        pass
