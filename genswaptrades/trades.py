#!/usr/bin/env python
# coding=utf-8
#
# trades functionality
#
import logging
from typing import List, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def generate_trades(fname: str,
                    min_rate: float = -0.1,
                    max_rate: float = 0.1,
                    additional_trade_rates: List[float] | None = None
                    ) -> List[Tuple[int, float, float, float]]:
    """Generate interest rate swap trades to achieve zero-sum notional value and cashflow.

    Note
    ----
    If 1 trade is sufficient to achieve the zero-sum, the rate is determined as the ratio
    between total cashflow and total notional value, after proper rounding.

    If 2 trades are necessary to achieve the zero-sum, the two rates used are
    0.1 and 0.05 by default, or the two floats in `additional_trade_rates` if it is passed in input.

    Args:
        fname (str): Filename containing the trades.
        min_rate (float, optional): minimum allowed trade rate. Default: -0.1.
        max_rate (float, optional): maximum allowed trade rate. Default: 0.1.
        additional_trade_rates (list[float], optional): if 2 trades are necessary to achieve zero-sum, the rates of these two trades. Default: None.
            If None, they default to [max_rate, max_rate - 0.1 * (max_rate - min_rate)]. They must be different and can take any float value within [min_rate, max_rate].

    Returns:
        List[Tuple[int, float, float, float]]: list of tuples with all the generated trades,
          one Tuple (trade no., notional, rate, cashflow) for each trade.
    """
    if not additional_trade_rates:
        # set additional_trade_rates dynamically (avoid mutable default argument value)
        additional_trade_rates = [max_rate, max_rate - 0.1 * (max_rate - min_rate)]
    else:
        assert additional_trade_rates[0] != additional_trade_rates[1], f"Expect different trade rates, got {additional_trade_rates}"
        assert all(additional_trade_rates) != 0, f"Expect non-zero trade rates, got {additional_trade_rates}"

    # check that the additional_trade_rates are within [min_rate, max_rate] interval
    for rate in additional_trade_rates:
        assert min_rate <= rate <= max_rate, \
            f"Expect additional_trade_rate to be in [{min_rate},{max_rate}], got {rate}."

    # round the input min_rate, max_rate values to 8 digits
    min_rate = np.round(min_rate, 8)
    max_rate = np.round(max_rate, 8)

    # read trades and compute total notional and cashflow, after rounding them.
    df = pd.read_csv(fname)
    df['cashflow'] = df['notional'] * df['rate']
    df['cashflow_rounded'] = df['cashflow'].round(2)
    notional_rounded_sum = np.round(df['notional'].sum(), 2)
    cashflow_rounded_sum = np.round(df['cashflow_rounded'].sum(), 2)
    Ntrades = len(df)

    # exit if both notional and cashflow are already 0.00
    if notional_rounded_sum == 0. and cashflow_rounded_sum == 0.:
        logging.info("notional and cashflow are already 0.00. No new trades are necessary.")
        return []

    new_trades = []

    logger.info(f"Starting the trade generation for input file {fname}: {Ntrades} trades found.")
    logger.info(f"Initial notional_sum={notional_rounded_sum} and cashflow_sum={cashflow_rounded_sum}.")

    # compute the rate for the next trade to achieve zero-sum notional and cashflow.
    if notional_rounded_sum != 0:
        next_trade_rate = cashflow_rounded_sum / notional_rounded_sum
        next_trade_rounded_rate = np.round(cashflow_rounded_sum / notional_rounded_sum, 8)
        logger.info(f"The rate of a single trade needed to achieve zero-sum is {next_trade_rate:11.8f}")
    else:
        next_trade_rate = next_trade_rounded_rate = np.inf
        logger.info("Notional sum is already 0.00. Two trades are necessary.")

    if next_trade_rounded_rate < min_rate or next_trade_rounded_rate > max_rate:
        # more than 1 trade is necessary, ensure that we can make it in 2 trades
        logger.info(f"The single-trade rate is outside of [{min_rate:11.8f}, {max_rate:11.8f}] interval: 2 trades are necessary.")

        trade_1_rate, trade_2_rate = additional_trade_rates

        # the first trade is done at trade_1_rate
        Ntrades += 1
        trade_1_notional = np.round(
            (notional_rounded_sum * trade_2_rate - cashflow_rounded_sum) / (trade_1_rate - trade_2_rate),
            2
        )
        trade_1_cashflow = np.round(trade_1_notional * trade_1_rate, 2)
        new_trades.append(
            (Ntrades, trade_1_notional, trade_1_rate, trade_1_cashflow)
        )

        # the second trade is done at trade_2_rate
        Ntrades += 1
        trade_2_notional = np.round(-trade_1_notional - notional_rounded_sum, 2)
        trade_2_cashflow = np.round(trade_2_notional * trade_2_rate, 2)
        new_trades.append(
            (Ntrades, trade_2_notional, trade_2_rate, trade_2_cashflow)
        )

    else:
        # 1 trade is sufficient as next_rate is within [min_rate, max_rate].
        logger.info("The single-trade rate is within of [min_rate, max_rate] interval: 1 trade is sufficient.")

        Ntrades += 1
        new_trades.append(
            (Ntrades, -notional_rounded_sum, np.round(next_trade_rate, 8), -cashflow_rounded_sum)
        )
        logger.info("Number of generated trades: 1")

    for new_trade in new_trades:
        notional_rounded_sum += np.round(new_trade[1], 2)
        cashflow_rounded_sum += np.round(new_trade[3], 2)

    # ensure that zero-sum notional and cashflow has been achieved
    assert np.abs(notional_rounded_sum) < 0.01
    assert np.abs(cashflow_rounded_sum) < 0.01

    logger.info(
        f"Final notional_sum and cashflow_sum are expected to be both zero (i.e. < 0.01), got notional_sum={notional_rounded_sum:<15.2f} and cashflow_sum={cashflow_rounded_sum:<15.2f}")
    logger.info("Output columns, 1 row for each trade: Trade <trade no.>  <notional value>  <rate>  <cashflow>")

    return new_trades


def format_trades(trades: List[Tuple[int, float, float, float]]) -> str:
    """Format the generated trades with the desired formatting.

    Output format is one line per trade:
      `Trade <trade no>  <notional>  <rate>  <cashflow>

    Args:
        trades (List[Tuple[int, float, float, float]]): list of tuples with all the generated trades,
          one Tuple (trade no., notional, rate, cashflow) for each trade.
    """
    return "\n".join(["Trade {}   {:15.2f}  {:11.8f}  {:15.2f}".format(*trade) for trade in trades])


def print_trades(trades: List[Tuple[int, float, float, float]]) -> None:
    """Print the text-formatted generated trades.

    Args:
        trades (List[Tuple[int, float, float, float]]): list of tuples with all the generated trades,
          one Tuple (trade no., notional, rate, cashflow) for each trade.
    """
    if trades:
        print(format_trades(trades))
