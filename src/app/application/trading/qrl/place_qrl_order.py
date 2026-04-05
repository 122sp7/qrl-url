from dataclasses import dataclass

from src.app.application.ports.exchange_service import ExchangeServiceFactory, PlaceOrderRequest
from src.app.application.trading.use_cases.place_order import _serialize_order
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.qrl_quantity import QrlQuantity
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce


@dataclass(frozen=True)
class PlaceQrlOrderCommand:
    """Command carrying all validated VOs needed to place a QRL/USDT order."""

    side: Side
    order_type: OrderType
    quantity: QrlQuantity
    price: QrlPrice | None = None
    time_in_force: TimeInForce | None = None
    client_order_id: str | None = None


class PlaceQrlOrder:
    """Place QRL/USDT order with fixed symbol and validated VOs."""

    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(self, command: PlaceQrlOrderCommand) -> dict:
        price_vo = Price.from_single(command.price.value) if command.price else None
        quantity_vo = Quantity(command.quantity.value)
        request = PlaceOrderRequest(
            symbol=Symbol("QRLUSDT"),
            side=command.side,
            order_type=command.order_type,
            price=price_vo,
            quantity=quantity_vo,
            time_in_force=command.time_in_force,
            client_order_id=command.client_order_id,
        )
        async with self._exchange_factory() as exchange:
            order = await exchange.place_order(request)
        return _serialize_order(order)
