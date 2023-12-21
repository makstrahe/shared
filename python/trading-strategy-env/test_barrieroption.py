import barrieroption
import unittest


def test_price():

    is_put = True
    strike = 100.0
    barrier = 80.0
    tenor = 1.0

    spot = 100.0
    ir = 0.02
    div_rate = 0.03
    vol = 0.2
    type_flag = "di"

    barrier_option = barrieroption.BarrierOption(is_put, strike, barrier, tenor)

    price_american = barrier_option.price_american(spot, ir, div_rate, vol, type_flag)
    price_american_benchmark = 6.28310517667393
    price_european = barrier_option.price_european_down_in(spot, ir, div_rate, vol)
    price_european_benchmark = 4.552140322347231

    tc = unittest.TestCase()
    tc.assertAlmostEqual(price_american, price_american_benchmark)
    tc.assertAlmostEqual(price_european, price_european_benchmark)
