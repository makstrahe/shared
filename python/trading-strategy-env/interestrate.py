import math
from curveinstrument import *
from marketdata import MarketData
from decimal import Decimal


class InterestRateIndex(CurveInstrument):
    def __init__(self, rate_index: RateIndex, currency: Currency, tenor_in_days: Decimal, quoted_price: float):
        super().__init__(quoted_price)
        self.rate_index = rate_index
        self.currency = currency
        self.tenor_in_days = tenor_in_days

    def tenor(self):
        return self.tenor_in_days/365


class InterestRateSwap(CurveInstrument):
    def __init__(self, rate_index: RateIndex, currency: Currency, tenor_in_months: Decimal,
                 float_leg_period_in_months: int, fixed_leg_period_in_months: int, quoted_price: float):
        super().__init__(quoted_price)
        self.rate_index = rate_index
        self.currency = currency
        self.tenor_in_months = tenor_in_months
        self.float_leg_period_in_months = float_leg_period_in_months
        self.fixed_leg_period_in_months = fixed_leg_period_in_months

    def tenor(self):
        return self.tenor_in_months/12


class DiscountCurve(MarketData):
    def __init__(self, currency: Currency, curve_instruments: list):
        super().__init__(str(currency))
        self.curve_instruments = sorted(curve_instruments, key=lambda x: x.tenor())

    def bootstrap(self):
        pass

    def calculate_zero_rate(self, tenor: Decimal):
        curve_instrument = self.curve_instruments[0]
        quoted_price = curve_instrument.get_quoted_price()

        return -1.0/float(tenor) * math.log(1.0/(1.0+quoted_price*tenor))

    def calculate_discount_factor(self, tenor: Decimal):
        curve_instrument = self.curve_instruments[0]
        quoted_price = curve_instrument.get_quoted_price()

        return 1.0/(1.0+quoted_price*tenor)
