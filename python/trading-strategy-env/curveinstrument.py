from abc import abstractmethod
from enum import Enum


class RateIndex(Enum):
    SARON = 1
    ESTR = 2
    SOFR = 3
    LIBOR = 4
    EURIBOR = 5


class Currency(Enum):
    USD = 1
    EUR = 2
    CHF = 3
    GBP = 4
    JPY = 5


class CurveInstrument:
    def __init__(self, quoted_price: float):
        self.quoted_price = quoted_price

    def get_quoted_price(self):
        return self.quoted_price

    @abstractmethod
    def tenor(self):
        pass
