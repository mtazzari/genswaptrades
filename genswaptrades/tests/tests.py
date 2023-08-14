#!/usr/bin/env python
# coding=utf-8
#
# genswaptrades tests
#
import os

import pytest

from genswaptrades.tests import TEST_ASSETS_DIR
from genswaptrades.trades import generate_trades


def test_same_additional_rates():
    """Test that AssertionError is raised if user provides two identical additional rates.
    In this case, if 2 trades are necessary, the linear system used to compute them will have no solution.
    """
    additional_trade_rates = [0.02324343, 0.02324343]

    with pytest.raises(AssertionError) as e:
        generate_trades(
            os.path.join(TEST_ASSETS_DIR, "trades1.csv"),
            additional_trade_rates=additional_trade_rates,
        )

    assert f"Expect different trade rates, got {additional_trade_rates}" == str(e.value)


def test_zero_additional_rates():
    """Test that AssertionError is raised if user provides a zero trade rate.
    In this case, if 2 trades are necessary, the linear system used to compute them will have no solution.
    """
    additional_trade_rates = [0., 0.02324343]
    with pytest.raises(AssertionError) as e:
        generate_trades(
            os.path.join(TEST_ASSETS_DIR, "trades1.csv"),
            additional_trade_rates=additional_trade_rates,
        )

    assert f"Expect non-zero trade rates, got {additional_trade_rates}" == str(e.value)

    additional_trade_rates = [0.02324343, 0.]
    with pytest.raises(AssertionError) as e:
        generate_trades(
            os.path.join(TEST_ASSETS_DIR, "trades1.csv"),
            additional_trade_rates=additional_trade_rates,
        )

    assert f"Expect non-zero trade rates, got {additional_trade_rates}" == str(e.value)


# what happens if empty file


# that gives correct result for different cases of notional/cashflow:
# positive/positive, pos/neg, neg/pos, neg/neg

# that gives correct result if the SUM notional/cashflow are:
# 0/... or .../0

# that it does 1 trade if rate equals max_rate
# that it does 1 trade if rate equals min_rate
