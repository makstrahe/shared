import datetime
import string
from curveinstrument import Currency


class Market:
    def __init__(self, valuation_date: datetime.date):
        self.valuation_date = valuation_date
        self.equity_spots = list()
        self.aggregate_equity_spots = list()
        self.discount_curves = list()
        self.dividend_curves = list()
        self.volatility_surfaces = list()

    @staticmethod
    def __check_item_exists(market_object, market_object_container: list):
        return market_object.id in [o.id for o in market_object_container]

    def add_equity_spot(self, spot):
        if not self.__check_item_exists(spot, self.equity_spots):
            self.equity_spots.append(spot)

    def add_aggregate_equity_spot(self, aggregate_spot):
        if not self.__check_item_exists(aggregate_spot, self.aggregate_equity_spots):
            self.aggregate_equity_spots.append(aggregate_spot)

    def add_discount_curve(self, discount_curve):
        if not self.__check_item_exists(discount_curve, self.discount_curves):
            self.discount_curves.append(discount_curve)

    def add_dividend_curve(self, dividend_curve):
        if not self.__check_item_exists(dividend_curve, self.dividend_curves):
            self.dividend_curves.append(dividend_curve)

    def add_volatility_surface(self, volatility_surface):
        if not self.__check_item_exists(volatility_surface, self.volatility_surfaces):
            self.volatility_surfaces.append(volatility_surface)

    def get_equity_spot(self, underlying_name: string):
        return [s for s in self.equity_spots if s.id == underlying_name].pop()

    def get_aggregate_equity_spot(self, underlying_name: string):
        return [s for s in self.aggregate_equity_spots if s.id == underlying_name].pop()

    def get_discount_curve(self, currency: Currency):
        return [s for s in self.discount_curves if s.id == str(currency)].pop()

    def get_dividend_curve(self, underlying_name: string):
        return [s for s in self.dividend_curves if s.id == underlying_name].pop()

    def get_volatility_surface(self, underlying_name: string):
        return [s for s in self.volatility_surfaces if s.id == underlying_name].pop()
