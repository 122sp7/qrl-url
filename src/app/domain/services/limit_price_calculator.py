from decimal import Decimal

from src.app.domain.value_objects.order_book import OrderBook
from src.app.domain.value_objects.side import Side


class LimitPriceCalculator:
    """Determine a maker-style limit price that does not cross the spread."""

    def __init__(self, buffer_pct: Decimal = Decimal("0.001")):
        self._buffer_pct = buffer_pct

    def compute(self, side: Side, order_book: OrderBook) -> Decimal | None:
        best_bid = self._best_bid(order_book)
        best_ask = self._best_ask(order_book)
        if best_bid <= 0 or best_ask <= 0 or best_bid >= best_ask:
            return None
        if side.value == "BUY":
            candidate = best_bid * (Decimal("1") - self._buffer_pct)
            return candidate if candidate < best_ask else None
        candidate = best_ask * (Decimal("1") + self._buffer_pct)
        return candidate if candidate > best_bid else None

    @staticmethod
    def _best_bid(book: OrderBook) -> Decimal:
        bids = [level.price for level in book.bids]
        return max(bids) if bids else Decimal("0")

    @staticmethod
    def _best_ask(book: OrderBook) -> Decimal:
        asks = [level.price for level in book.asks]
        return min(asks) if asks else Decimal("0")

    def best_price(self, side: Side, order_book: OrderBook) -> Decimal:
        """Return the best available price for the given side (min ask for BUY, max bid for SELL)."""
        if side.value == "BUY":
            prices = [level.price for level in order_book.asks]
            return min(prices) if prices else Decimal("0")
        prices = [level.price for level in order_book.bids]
        return max(prices) if prices else Decimal("0")
