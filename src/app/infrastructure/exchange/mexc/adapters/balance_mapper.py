from decimal import Decimal

from src.app.domain.events.balance_event import BalanceEvent
from src.app.infrastructure.exchange.mexc.generated import PrivateAccountV3Api_pb2


def balance_proto_to_domain(
    proto: PrivateAccountV3Api_pb2.PrivateAccountV3ApiBalance,
) -> BalanceEvent:
    return BalanceEvent(
        asset=proto.asset,
        free=Decimal(proto.free),
        locked=Decimal(proto.locked),
        timestamp=proto.timestamp,
    )
