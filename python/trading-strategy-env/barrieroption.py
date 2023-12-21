import math
from scipy.stats import norm


class BarrierOption:

    def __init__(self, is_put: bool, relative_strike: float, relative_barrier: float, tenor: float):

        self.is_put = is_put
        self.relative_strike = relative_strike
        self.relative_barrier = relative_barrier
        self.tenor = tenor

    def set_tenor(self, tenor: float):
        self.tenor = tenor

    def price_european_down_in(self, spot: float, ir: float, div_rate: float, vol: float):

        x = self.relative_strike * spot
        h = self.relative_barrier * spot
        t = self.tenor
        is_put = self.is_put

        s = spot
        r = ir
        v = vol
        b = ir - div_rate

        d1 = (math.log(s / h) + (b + v ** 2 / 2) * t) / (v * math.sqrt(t))
        d2 = d1 - v * math.sqrt(t)

        if not is_put:
            return s * math.exp((b - r) * t) * norm.cdf(d1) - x * math.exp(-r * t) * norm.cdf(d2)
        else:
            return x * math.exp(-r * t) * norm.cdf(-d2) - s * math.exp((b - r) * t) * norm.cdf(-d1)

    def price_american(self, spot: float, ir: float, div_rate: float, vol: float, type_flag: str):

        # TypeFlag:     The "TypeFlag" gives you 8 different standard barrier options:
        #               1) "di"=Down-and-in,    3) "ui"=Up-and-in
        #               2) "do"=Down-and-out,    4) "uo"=Up-out-in

        x = self.relative_strike * spot
        h = self.relative_barrier * spot
        t = self.tenor
        type_flag = "p" + type_flag if self.is_put else "c" + type_flag

        s = spot
        r = ir
        v = vol
        b = ir - div_rate
        mu = (b - v ** 2 / 2) / v ** 2
        _lambda = math.sqrt(mu ** 2 + 2 * r / v ** 2)

        x1 = math.log(s / x) / (v * math.sqrt(t)) + (1 + mu) * v * math.sqrt(t)
        x2 = math.log(s / h) / (v * math.sqrt(t)) + (1 + mu) * v * math.sqrt(t)
        y1 = math.log(h ** 2 / (s * x)) / (v * math.sqrt(t)) + (1 + mu) * v * math.sqrt(t)
        y2 = math.log(h / s) / (v * math.sqrt(t)) + (1 + mu) * v * math.sqrt(t)
        z = math.log(h / s) / (v * math.sqrt(t)) + _lambda * v * math.sqrt(t)

        if type_flag == "cdi" or type_flag == "cdo":
            eta = 1.0
            phi = 1.0
        elif type_flag == "cui" or type_flag == "cuo":
            eta = -1.0
            phi = 1.0
        elif type_flag == "pdi" or type_flag == "pdo":
            eta = 1.0
            phi = -1.0
        elif type_flag == "pui" or type_flag == "puo":
            eta = -1.0
            phi = -1.0
        else:
            raise Exception("Unknown barrier option type")

        k = 0

        f1 = phi * s * math.exp((b - r) * t) * norm.cdf(phi * x1) \
            - phi * x * math.exp(-r * t) * norm.cdf(phi * x1 - phi * v * math.sqrt(t))
        f2 = phi * s * math.exp((b - r) * t) * norm.cdf(phi * x2) \
            - phi * x * math.exp(-r * t) * norm.cdf(phi * x2 - phi * v * math.sqrt(t))
        f3 = phi * s * math.exp((b - r) * t) * (h / s) ** (2 * (mu + 1)) * norm.cdf(eta * y1) \
            - phi * x * math.exp(-r * t) * (h / s) ** (2 * mu) * norm.cdf(eta * y1 - eta * v * math.sqrt(t))
        f4 = phi * s * math.exp((b - r) * t) * (h / s) ** (2 * (mu + 1)) * norm.cdf(eta * y2) \
            - phi * x * math.exp(-r * t) * (h / s) ** (2 * mu) * norm.cdf(eta * y2 - eta * v * math.sqrt(t))
        f5 = k * math.exp(-r * t) * (norm.cdf(eta * x2 - eta * v * math.sqrt(t))
                                     - (h / s) ** (2 * mu) * norm.cdf(eta * y2 - eta * v * math.sqrt(t)))
        f6 = k * ((h / s) ** (mu + _lambda) * norm.cdf(eta * z)
                  + (h / s) ** (mu - _lambda) * norm.cdf(eta * z - 2 * eta * _lambda * v * math.sqrt(t)))

        if x > h:
            if type_flag == "cdi":
                return f3 + f5
            elif type_flag == "cui":
                return f1 + f5
            elif type_flag == "pdi":
                return f2 - f3 + f4 + f5
            elif type_flag == "pui":
                return f1 - f2 + f4 + f5
            elif type_flag == "cdo":
                return f1 - f3 + f6
            elif type_flag == "cuo":
                return f6
            elif type_flag == "pdo":
                return f1 - f2 + f3 - f4 + f6
            elif type_flag == "puo":
                return f2 - f4 + f6
            else:
                raise Exception("Unknown type flag")

        elif x <= h:
            if type_flag == "cdi":
                return f1 - f2 + f4 + f5
            elif type_flag == "cui":
                return f2 - f3 + f4 + f5
            elif type_flag == "pdi":
                return f1 + f5
            elif type_flag == "pui":
                return f3 + f5
            elif type_flag == "cdo":
                return f2 + f6 - f4
            elif type_flag == "cuo":
                return f1 - f2 + f3 - f4 + f6
            elif type_flag == "pdo":
                return f6
            elif type_flag == "puo":
                return f1 - f3 + f6
            else:
                raise Exception("Unknown type flag")
