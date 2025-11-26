import os
import uuid
import boto3
from dataclasses import dataclass
from typing import List, Any
from decimal import Decimal, InvalidOperation

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

@dataclass
class Item:
    id: str
    name: str
    price: float


def create_item(name: str, price: Any) -> Item:
    if not name or not name.strip():
        raise ValueError("name is required")

    # Convertir precio a Decimal (obligatorio para DynamoDB)
    try:
        price_decimal = Decimal(str(price))
    except InvalidOperation:
        raise ValueError("price must be a number")

    if price_decimal < 0:
        raise ValueError("price must be >= 0")

    item = Item(
        id=str(uuid.uuid4()),
        name=name.strip(),
        price=float(price_decimal)  # para devolver como float en la API
    )

    # Guardar en DynamoDB usando Decimal
    table.put_item(Item={
        "id": item.id,
        "name": item.name,
        "price": price_decimal
    })

    return item


def list_items() -> List[Item]:
    response = table.scan()
    items = response.get("Items", [])

    result = []
    for i in items:
        result.append(
            Item(
                id=i["id"],
                name=i["name"],
                price=float(i["price"])  # DynamoDB devuelve Decimal → convertir a float
            )
        )
    return result
