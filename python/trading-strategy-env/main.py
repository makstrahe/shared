from smiportfoliosimulation import *

if __name__ == '__main__':

    # option details
    is_put = True
    relative_strike = 1.0
    relative_barrier = 0.8
    tenor = 1.0

    # underlying names universe
    underlying_names_universe = ["SMI", "NESN", "NOVN", "ROG", "UBSG", "ZURN", "CSGN"]

    # read data from files and construct markets
    markets = construct_markets_from_data(underlying_names_universe)

    # historical simulation of underlying universe
    dip_portfolio_result_df = historically_simulate_dip_portfolio(markets, underlying_names_universe, is_put,
                                                                  relative_strike, relative_barrier, tenor)

    # construction of sub-portfolio
    underlying_names_portfolio = ["NESN", "NOVN", "ROG", "UBSG"]
    portfolio_weights = [0.28, 0.28, 0.28, 0.08]
    result = construct_portfolio_df(underlying_names_portfolio, portfolio_weights, dip_portfolio_result_df)
