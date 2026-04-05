from src.app.domain.events.market_depth_event import MarketDepthEvent
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.symbol import Symbol
from src.app.infrastructure.exchange.mexc.generated import PublicAggreDepthsV3Api_pb2


def depth_proto_to_domain(
    symbol: Symbol, proto: PublicAggreDepthsV3Api_pb2.PublicAggreDepthsV3Api
) -> MarketDepthEvent:
    bids = [
        (Price(float(item.price)), Quantity(float(item.quantity))) for item in proto.bids
    ]
    asks = [
        (Price(float(item.price)), Quantity(float(item.quantity))) for item in proto.asks
    ]

    return MarketDepthEvent(
        symbol=symbol,
        bids=bids,
        asks=asks,
        event_type=proto.eventType if hasattr(proto, "eventType") else None,
        from_version=proto.fromVersion if hasattr(proto, "fromVersion") else None,
        to_version=proto.toVersion if hasattr(proto, "toVersion") else None,
    )
