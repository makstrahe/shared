import datetime
import string
import numpy
from decimal import Decimal
from datetimeextensions import DateTimeExtensions as Dte
from interpolation import Interpolator2d
from marketdata import MarketData
from volatilitypoint import TradeSide, VolatilitySlice, Volatility


class VolatilitySurface(MarketData):
    def __init__(self, underlying_name: string, tenor_in_months_grid: list, moneyness_grid: list, volatilities: numpy.array):
        super().__init__(underlying_name)
        self.tenor_in_months_grid = tenor_in_months_grid
        self.moneyness_grid = moneyness_grid
        self.volatilities = volatilities

    @classmethod
    def from_volatility_points(cls, underlying_name: string, volatility_points: list):
        tenors_in_months = sorted(list(set([p.tenor_in_months for p in volatility_points])))
        volatility_slices = list()
        for e in tenors_in_months:
            volatility_slices.append(VolatilitySlice([p for p in volatility_points if p.tenor_in_months == e]))

        return cls.from_volatility_slices(underlying_name, volatility_slices)

    @classmethod
    def from_volatility_slices(cls, underlying_name: string, volatility_slices: list):
        tenor_in_months_grid = [p.tenor_in_months for p in volatility_slices]
        moneyness_grid = volatility_slices[0].get_moneyness_grid()
        if not all(s.get_moneyness_grid() == moneyness_grid for s in volatility_slices):
            raise Exception("Cannot make homogeneous volatility surface: moneyness grids differ for different tenors")
        volatilities = numpy.empty((len(tenor_in_months_grid), len(moneyness_grid)), dtype=Volatility)
        for i, s in enumerate(volatility_slices):
            for j, m in enumerate(moneyness_grid):
                volatilities[i, j] = s.get_volatility_grid()[j]

        return cls(underlying_name, tenor_in_months_grid, moneyness_grid, volatilities)

    def get_volatilities(self, valuation_date: datetime.date, expirydate_moneyness_list: list, trade_side: TradeSide):
        tenor_moneyness_list = [(Dte.difference_in_months(valuation_date, e[0]), e[1])
                                for e in expirydate_moneyness_list]

        return self.get_volatilities(tenor_moneyness_list, trade_side)

    def get_volatilities(self, tenor_moneyness_list: list, trade_side: TradeSide):
        used_vol_array = numpy.empty(shape=[self.volatilities.shape[0], self.volatilities.shape[1]])
        for i in range(self.volatilities.shape[0]):
            for j in range(self.volatilities.shape[1]):
                if trade_side == TradeSide.BID:
                    used_vol_array[i, j] = self.volatilities[i, j].bid_value
                elif trade_side == TradeSide.ASK:
                    used_vol_array[i, j] = self.volatilities[i, j].ask_value
                elif trade_side == TradeSide.MID:
                    used_vol_array[i, j] = self.volatilities[i, j].mid_value()
                else:
                    raise Exception("Unknown trade side type")

        interpolator = Interpolator2d([float(t) for t in self.tenor_in_months_grid],
                                      [float(m) for m in self.moneyness_grid], used_vol_array)
        tenor_in_months_moneyness_list = [(float(tm[0]*12), float(tm[1])) for tm in tenor_moneyness_list]

        return interpolator(tenor_in_months_moneyness_list)

    def get_volatility(self, tenor: Decimal, moneyness: Decimal, trade_side: TradeSide):
        volatilities = self.get_volatilities([(tenor, moneyness)], trade_side)
        return volatilities.pop()
