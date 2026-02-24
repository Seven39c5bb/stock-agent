from typing import Tuple

import numpy as np


def calc_slope(prices: np.ndarray) -> float:
    if prices.size < 2:
        return 0.0
    x = np.arange(prices.size, dtype=float)
    slope, _ = np.polyfit(x, prices, 1)
    return float(slope)


def calc_volatility(prices: np.ndarray) -> float:
    if prices.size < 2:
        return 0.0
    returns = np.diff(prices) / prices[:-1]
    if returns.size < 2:
        return 0.0
    return float(np.std(returns, ddof=1) * np.sqrt(252))


def calc_support_resistance(prices: np.ndarray) -> Tuple[float, float]:
    if prices.size == 0:
        return 0.0, 0.0
    return float(np.min(prices)), float(np.max(prices))
