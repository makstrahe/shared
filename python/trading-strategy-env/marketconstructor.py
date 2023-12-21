import pandas as pd
from curveinstrument import Currency
from market import Market
from tablemarketdataconverter import TableMarketDataConverter as Tc


class MarketConstructor:
    @staticmethod
    def timeseries_from_dataframes(market_dataframe_dict: dict):
        # find common dates in all underlyings
        historical_dates = [t.date() for t in list(market_dataframe_dict.values())[0].index.to_list()]
        for d in list(market_dataframe_dict.values()):
            historical_dates = list(set(historical_dates).intersection([t.date() for t in d.index.to_list()]))
        historical_dates.sort()
        markets = list()
        for d in historical_dates:
            market = Market(d)
            MarketConstructor.__add_market_objects(market, market_dataframe_dict)
            markets.append(market)

        return markets

    @staticmethod
    def merge_dataframes(equity_market_dataframe_dicts: list, rate_market_dataframe_dict: dict):
        underlyings = equity_market_dataframe_dicts[0].keys()
        md_dict = dict()
        for u in underlyings:
            md_dict[u] = equity_market_dataframe_dicts[0][u]
            for d in equity_market_dataframe_dicts[1:]:
                md_dict[u] = pd.merge(md_dict[u], d[u], left_index=True, right_index=True)
                for k, v in rate_market_dataframe_dict.items():
                    md_dict[u] = pd.merge(md_dict[u], v, left_index=True, right_index=True)

        return md_dict

    @staticmethod
    def __add_market_objects(market: Market, equity_market_dataframe_dict: dict):
        for n, df in equity_market_dataframe_dict.items():
            single_md_series = df.loc[market.valuation_date.strftime("%Y-%m-%d")]
            market.add_discount_curve(Tc.convert_discount_curve_data(Currency.CHF, single_md_series))
            market.add_equity_spot(Tc.convert_equity_spot_data(n, single_md_series))
            market.add_aggregate_equity_spot(Tc.convert_equity_spot_aggregate_data(n, single_md_series))
            market.add_dividend_curve(Tc.convert_dividend_curve_data(n, single_md_series))
            market.add_volatility_surface(Tc.convert_volatility_data_to_surface(n, single_md_series))
