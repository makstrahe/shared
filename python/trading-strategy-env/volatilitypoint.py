import decimal
from enum import Enum


class TradeSide(Enum):
    MID = 1
    BID = 2
    ASK = 3


class Volatility:
    def __init__(self, bid_value=None, ask_value=None):
        self.bid_value = bid_value
        self.ask_value = ask_value

    def set_ask_value(self, ask_value: float):
        self.ask_value = ask_value

    def set_bid_value(self, bid_value: float):
        self.bid_value = bid_value

    def mid_value(self):
        bid_value = self.ask_value if self.bid_value is None else self.bid_value
        ask_value = self.bid_value if self.ask_value is None else self.ask_value
        return (bid_value + ask_value) / 2.0


class VolatilityPoint:
    def __init__(self, tenor_in_months: decimal, moneyness: decimal, volatility: Volatility):
        self.tenor_in_months = tenor_in_months
        self.moneyness = moneyness
        self.volatility = volatility


class VolatilitySlice:
    def __init__(self, volatility_points: list):
        self.volatility_points = sorted(volatility_points, key=lambda x: x.moneyness)
        self.tenor_in_months = volatility_points[0].tenor_in_months
        if not all(p.tenor_in_months == self.tenor_in_months for p in volatility_points):
            raise Exception("Volatility points do not reside on single strike slice")

    def get_moneyness_grid(self):
        return [p.moneyness for p in self.volatility_points]

    def get_volatility_grid(self):
        return [p.volatility for p in self.volatility_points]
