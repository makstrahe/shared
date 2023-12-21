import string
import pandas
from barrieroption import BarrierOption
from filereader import CsvFileReader
from historicalsimulation import HistoricalSimulation
from marketconstructor import MarketConstructor


def construct_markets_from_data(underlying_names):
    # gather data
    rate_data_path = "I:\\Organisation\\ZK_Alle\\BacktestPortfolioVersusIndex\\DataRate"
    spotdiv_data_path = "I:\\Organisation\\ZK_Alle\\BacktestPortfolioVersusIndex\\DataSpotDiv"
    vol_data_path = "I:\\Organisation\\ZK_Alle\\BacktestPortfolioVersusIndex\\DataVol"

    rate_dfs = CsvFileReader(rate_data_path, ';').create_timeseries_dataframe_dict("Dates")
    equity_spotdiv_dfs = CsvFileReader(spotdiv_data_path, ';').create_timeseries_dataframe_dict("Dates")
    equity_vol_dfs = CsvFileReader(vol_data_path, ';').create_timeseries_dataframe_dict("Datum")

    # construct timeseries of markets
    equity_market_df_dicts = [equity_spotdiv_dfs, equity_vol_dfs]
    rate_market_df_dict = rate_dfs
    market_dataframe_dict = MarketConstructor.merge_dataframes(equity_market_df_dicts, rate_market_df_dict)
    market_dataframe_dict = {u: market_dataframe_dict[u] for u in underlying_names}
    markets = MarketConstructor.timeseries_from_dataframes(market_dataframe_dict)

    return markets


def historically_simulate_dip_portfolio(markets: list, underlying_names: string,
                                        is_put: bool, relative_strike: float, relative_barrier: float, tenor: float):
    hist_sim = HistoricalSimulation(markets)
    barrier_option = BarrierOption(is_put, relative_strike, relative_barrier, tenor)
    dip_portfolio_result_df = hist_sim.simulate_dip_portfolio(underlying_names, barrier_option)

    return dip_portfolio_result_df


def construct_portfolio_df(underlying_names: list, pf_weights: list, dip_df_dict: dict):
    portfolio_df = pf_weights[0] * dip_df_dict[underlying_names[0]][["optionPv", "optionPv%", "performance",
                                                                     "effectivePerformance", "pnl"]]
    barrier_hit_df = dip_df_dict[underlying_names[0]][["isBarrierHit"]].astype(int)
    for i, u in enumerate(underlying_names[1:], 1):
        portfolio_df += pf_weights[i] * dip_df_dict[u][["optionPv", "optionPv%", "performance", "effectivePerformance",
                                                        "pnl"]]
        barrier_hit_df += dip_df_dict[u][["isBarrierHit"]].astype(int)
    portfolio_df = pandas.merge(portfolio_df, barrier_hit_df, left_index=True, right_index=True)
    portfolio_df = pandas.merge(portfolio_df,
                                dip_df_dict[underlying_names[0]][["adjustedExpiryDate", "spot", "div", "rate",
                                "atmVol", "wingVol", "pricingVol"]],
                                left_index=True, right_index=True)

    return portfolio_df
