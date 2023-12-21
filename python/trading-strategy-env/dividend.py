import string
from datashape import Decimal
from curveinstrument import CurveInstrument
from marketdata import MarketData


class Dividend(CurveInstrument):
    def __init__(self, tenor_ex: Decimal, tenor_pay: Decimal, div_yield: float):
        # div_yield continuous compounded pa yield
        super().__init__(div_yield)
        self.tenor_ex = tenor_ex
        self.tenor_pay = tenor_pay

    def tenor(self):
        return self.tenor_ex


class DividendCurve(MarketData):
    def __init__(self, underlying_name: string, dividends: list):
        super().__init__(underlying_name)
        self.dividends = sorted(dividends, key=lambda x: x.tenor_ex)

    def calculate_zero_rate(self, tenor: Decimal):
        dividend = self.dividends[0]
        return dividend.quoted_price
