from dataclasses import dataclass

_MAX_CLIENT_ORDER_ID_LENGTH = 32


@dataclass(frozen=True)
class ClientOrderId:
    """Client-supplied idempotency key for orders."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Client order id cannot be empty")
        if len(self.value) > _MAX_CLIENT_ORDER_ID_LENGTH:
            raise ValueError("Client order id must be 32 characters or fewer")
