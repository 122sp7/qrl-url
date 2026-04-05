from dataclasses import dataclass

from src.app.domain.value_objects.order_id import OrderId
from src.app.domain.value_objects.order_status import OrderStatus
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.symbol import Symbol


@dataclass(frozen=True)
class OrderEvent:
    """Private order update event."""

    order_id: OrderId
    symbol: Symbol
    price: Price
    quantity: Quantity
    status: OrderStatus
    timestamp: int
