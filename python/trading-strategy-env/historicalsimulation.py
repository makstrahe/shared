import datetime
import string
import pandas as pd
from dateutil import relativedelta

from datetimeextensions import DateTimeExtensions as Dte
from barrieroption import BarrierOption
from curveinstrument import Currency
from market import Market
from volatilitypoint import TradeSide


class HistoricalSimulation:
    def __init__(self, markets: list):
        self.markets = markets

    def simulate_dip_portfolio(self, underlying_names: list, barrier_option: BarrierOption):
        underlying_df = dict()
        max_market_date = max([m.valuation_date for m in self.markets])
        orig_barrier_option_tenor = barrier_option.tenor

        for u in underlying_names:
            inception_dates, adjusted_expiry_dates, pvs, strike_performances, is_barrier_hits, eff_performances, pnls\
                = ([] for i in range(7))

            for m in self.markets:
                expiry_date = m.valuation_date + relativedelta.relativedelta(days=int(orig_barrier_option_tenor*365))
                if expiry_date > max_market_date + relativedelta.relativedelta(days=7):
                    break

                adjusted_expiry_date = min([m.valuation_date for m in self.markets],
                                           key=lambda d: abs(Dte.difference_in_years(d, expiry_date)))
                adjusted_tenor = Dte.difference_in_years(m.valuation_date, adjusted_expiry_date)
                barrier_option.set_tenor(adjusted_tenor)

                pv = self.price_barrier_option(m, u, barrier_option)

                strike_performance = self.strike_performance(m, u, barrier_option, adjusted_expiry_date)
                is_barrier_hit = self.is_barrier_hit(m, u, barrier_option, adjusted_expiry_date)
                eff_performance = strike_performance if is_barrier_hit else 0.0
                accrual_factor = 1.0 / m.get_discount_curve(Currency.CHF).calculate_discount_factor(adjusted_tenor)
                pnl = accrual_factor * pv[7] - (1.0 if is_barrier_hit else 0.0) * max(-strike_performance, 0.0)

                inception_dates.append(m.valuation_date)
                adjusted_expiry_dates.append(adjusted_expiry_date)
                pvs.append(pv)
                strike_performances.append(strike_performance)
                is_barrier_hits.append(is_barrier_hit)
                eff_performances.append(eff_performance)
                pnls.append(pnl)

            df_data = {"inceptionDate": inception_dates, "adjustedExpiryDate": adjusted_expiry_dates,
                       "spot": [r[0] for r in pvs], "div": [r[1] for r in pvs], "rate": [r[2] for r in pvs],
                       "atmVol": [r[3] for r in pvs], "wingVol": [r[4] for r in pvs], "pricingVol": [r[5] for r in pvs],
                       "optionPv": [r[6] for r in pvs], "optionPv%": [r[7] for r in pvs],
                       "performance": strike_performances, "isBarrierHit": is_barrier_hits,
                       "effectivePerformance": eff_performances, "pnl": pnls}
            df = pd.DataFrame(df_data).set_index("inceptionDate")
            df.index = pd.to_datetime(df.index, format="%Y-%m-%d")
            underlying_df[u] = df

        return underlying_df

    def simulate_smi_index(self):
        pass

    @staticmethod
    def price_barrier_option(inception_market: Market, underlying_name: string, barrier_option: BarrierOption):
        equity_spot = inception_market.get_equity_spot(underlying_name).quoted_price
        dividend_yield = inception_market.get_dividend_curve(underlying_name).calculate_zero_rate(barrier_option.tenor)
        discount_rate = inception_market.get_discount_curve(Currency.CHF).calculate_zero_rate(barrier_option.tenor)
        vol_surface = inception_market.get_volatility_surface(underlying_name)
        atm_vol = vol_surface.get_volatility(barrier_option.tenor, 1.0, TradeSide.MID)
        put_wing_vol = vol_surface.get_volatility(barrier_option.tenor, barrier_option.relative_barrier, TradeSide.MID)
        pricing_vol = 2 / 3 * atm_vol + 1 / 3 * put_wing_vol
        pv = barrier_option.price_american(equity_spot, discount_rate, dividend_yield, pricing_vol, "di")
        return [equity_spot, dividend_yield, discount_rate, atm_vol, put_wing_vol,
                pricing_vol, pv, pv / (barrier_option.relative_strike * equity_spot)]

    def strike_performance(self, inception_market: Market, underlying_name: string,
                           barrier_option: BarrierOption, adjusted_expiry_date: datetime.date):
        equity_spot_incept = inception_market.get_equity_spot(underlying_name).quoted_price
        equity_spot_expiry = [m for m in self.markets if m.valuation_date == adjusted_expiry_date].pop() \
            .get_equity_spot(underlying_name).quoted_price

        return equity_spot_expiry / (barrier_option.relative_strike * equity_spot_incept) - 1.0

    def is_barrier_hit(self, inception_market: Market, underlying_name: string,
                       barrier_option: BarrierOption, adjusted_expiry_date: datetime.date):
        equity_spot_incept = inception_market.get_equity_spot(underlying_name).quoted_price
        equity_spot_low = min([m.get_aggregate_equity_spot(underlying_name).min for m in self.markets if
                              adjusted_expiry_date >= m.valuation_date > inception_market.valuation_date])
        return True if equity_spot_low / equity_spot_incept < barrier_option.relative_barrier else False




