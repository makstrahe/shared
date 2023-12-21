import string
import pandas as pd
from dividend import Dividend, DividendCurve
from interestrate import *
from spot import VanillaEquity, VanillaEquityAggregate
from volatilitypoint import VolatilityPoint, Volatility
from volatilitysurface import VolatilitySurface
from decimal import Decimal


class TableMarketDataConverter:
    @staticmethod
    def convert_equity_spot_data(underlying_name: string, md_series: pd.Series):
        return VanillaEquity(underlying_name, md_series["PX_LAST"])

    @staticmethod
    def convert_equity_spot_aggregate_data(underlying_name: string, md_series: pd.Series):
        sa = VanillaEquityAggregate(underlying_name, backward_period_in_days=7)
        sa.set_min(md_series["PX_LOW"])
        return sa

    @staticmethod
    def convert_discount_curve_data(currency: Currency, md_series: pd.Series):
        chf_libor_12m = InterestRateIndex(RateIndex.LIBOR, currency, Decimal(365), md_series["SF0012M"] / 100.0)
        return DiscountCurve(currency, [chf_libor_12m])

    @staticmethod
    def convert_dividend_curve_data(underlying_name: string, md_series: pd.Series):
        equity_spot = md_series["PX_LAST"]
        div_yield = md_series["EQY_DVD_YLD_IND"] / 100.0
        continuous_compounded_div_yield = - math.log(1.0 - div_yield)
        dividend = Dividend(Decimal(1), Decimal(1), continuous_compounded_div_yield)
        return DividendCurve(underlying_name, [dividend])

    @staticmethod
    def convert_volatility_data_to_surface(underlying_name: string, md_series: pd.Series):
        vol_identifier = "Vol"
        volatility_data = md_series.filter(like=vol_identifier)
        volatility_points = list()
        vol_dict = dict()
        for k, v in volatility_data.items():
            tenor_str, moneyness_str, side = k.split("_")[1:]
            v /= 100.0
            if (tenor_str, moneyness_str) not in vol_dict:
                vol_dict[(tenor_str, moneyness_str)] = Volatility(bid_value=v) if side == 'Bid' \
                    else Volatility(ask_value=v)
            else:
                vol_dict[(tenor_str, moneyness_str)].set_bid_value(v) if side == "Bid" \
                    else vol_dict[(tenor_str, moneyness_str)].set_ask_value(v)

        for k, v in vol_dict.items():
            tenor_in_months = Decimal(k[0][:-1])
            moneyness = Decimal(k[1])/100
            volatility_points.append(VolatilityPoint(tenor_in_months, moneyness, v))

        return VolatilitySurface.from_volatility_points(underlying_name, volatility_points)
