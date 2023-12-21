import decimal
import string
from marketdata import MarketData


class VanillaEquity(MarketData):
    def __init__(self, underlying_name: string, quoted_price: float):
        super().__init__(underlying_name)
        self.quoted_price = quoted_price


class VanillaEquityAggregate(MarketData):
    def __init__(self, underlying_name: string, backward_period_in_days: decimal):
        super().__init__(underlying_name)
        self.backward_period_in_days = backward_period_in_days
        self.max = None
        self.min = None

    def set_max(self, max_value: float):
        self.max = max_value

    def set_min(self, min_value: float):
        self.min = min_value
