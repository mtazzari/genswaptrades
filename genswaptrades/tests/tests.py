#!/usr/bin/env python
# coding=utf-8
#
# genswaptrades tests
#
import os
import tempfile

import numpy as np
import pytest
from pandas.errors import EmptyDataError

from genswaptrades.tests import TEST_ASSETS_DIR
from genswaptrades.trades import format_trades, generate_trades

provided_tests_expected_results: dict[str, dict] = {
    "trades1.csv": {
        'api': [(3, -545891.29, 0.04889299, -26690.26)],
        'txt': "Trade 3        -545891.29   0.04889299        -26690.26",
        'comment': 'TEST PROVIDED BY PROBLEM: trades1.csv'
    },
    "trades2.csv": {
        'api': [(6, 3950072.95, 0.00134147, 5298.91)],
        'txt': "Trade 6        3950072.95   0.00134147          5298.91",
        'comment': 'TEST PROVIDED BY PROBLEM: trades2.csv'
    },
    "trades3.csv": {
        'api': [(5, -26409.6, 0.1, -2640.96), (6, 26483.0, 0.08, 2118.64)],
        'txt': "Trade 5         -26409.60   0.10000000         -2640.96\nTrade 6          26483.00   0.08000000          2118.64",
        'comment': 'TEST PROVIDED BY PROBLEM: trades3.csv; notional sum < 0 cashflows sum > 0'
    },
    "trades4.csv": {
        'api': [(6, 10073.4, 0.03970854, 400.0)],
        'txt': "Trade 6          10073.40   0.03970854           400.00",
        'comment': 'notional sum < 0 cashflows sum < 0'
    },
    "trades5.csv": {
        'api': [(7, -9926.6, -0.03828098, 380.0)],
        'txt': "Trade 7          -9926.60  -0.03828098           380.00",
        'comment': 'notional sum > 0 cashflows sum < 0'
    },
    "trades6.csv": {
        'api': [(8, -691280.1, 0.1, -69128.01), (9, 663341.5, 0.08, 53067.32)],
        'txt': "Trade 8        -691280.10   0.10000000        -69128.01\nTrade 9         663341.50   0.08000000         53067.32",
        'comment': 'notional sum > 0 cashflows sum > 0'
    },
    "trades7.csv": {
        'api': [(9, -663341.5, 0.1, -66334.15), (10, 663341.5, 0.08, 53067.32)],
        'txt': "Trade 9        -663341.50   0.10000000        -66334.15\nTrade 10         663341.50   0.08000000         53067.32",
        'comment': 'notional sum == 0 cashflows sum > 0; 2-trades needed because the 1-trade rate is inf'
    },
    "trades8.csv": {
        'api': [(10, 132668.36, 8e-08, 0.01)],
        'txt': "Trade 10         132668.36   0.00000008             0.01",
        'comment': 'notional sum < 0 cashflows sum == 0; a 1-trade with very small rate is sufficient to zero-sum notional'
    },
    "trades9.csv": {
        'api': [],
        'txt': "",
        'comment': 'notional sum == 0 cashflows sum == 0; no new trades are necessary'
    },
}


@pytest.mark.parametrize("test_input_fname,expected_results",
                         [(fname, data) for (fname, data) in provided_tests_expected_results.items()],
                         ids=[data['comment'] for (_, data) in provided_tests_expected_results.items()]
                         )
def test_provided_test_cases(test_input_fname: str, expected_results: dict) -> None:
    """Test that the output (both via API and as console output) matches the expected results, for the provided test cases.

    Args:
        test_input_fname (str): input filename.
        expected_results (dict): expected results dict containing the api and the text rendered expected result.
    """
    res_api = generate_trades(
        os.path.join(TEST_ASSETS_DIR, test_input_fname),
    )
    res_txt = format_trades(res_api)

    assert res_api == expected_results['api']
    assert res_txt == expected_results['txt']


def test_one_trade_rate_equals_trade_rates() -> None:
    """Test that the trades are generated as expected even if max_rate equals the 1-trade rate (at the 8 digit rounding precision).
    """
    # with pytest.raises(AssertionError) as e:
    res_api = generate_trades(
        os.path.join(TEST_ASSETS_DIR, "trades2.csv"),
        max_rate=0.00134147,
    )
    assert res_api == provided_tests_expected_results['trades2.csv']['api']


def test_switch_to_two_trades_if_one_trade_rate_larger_than_max_rate() -> None:
    """Test that the algorithm switches to 2-trades if the 1-trade rate is larger than max_rate (at the 8 digit rounding precision).
    """
    # here it should stick to 1-trade because the rate is identical to max_rate within 8-digit rounding precision.
    res_api = generate_trades(
        os.path.join(TEST_ASSETS_DIR, "trades2.csv"),
        max_rate=0.0013414699,
    )
    assert res_api == [(6, 3950072.95, 0.00134147, 5298.91)]

    # here it should switch to 2-trades
    res_api = generate_trades(
        os.path.join(TEST_ASSETS_DIR, "trades2.csv"),
        max_rate=0.00134146,
    )
    assert res_api == [(6, 3950077.4, 0.00134146, 5298.87), (7, -4.45, -0.008792686000000001, 0.04)]


def test_same_additional_rates() -> None:
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


def test_zero_additional_rates() -> None:
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


def test_empty_trades_file() -> None:
    """Test that a pandas EmptyDataError is raised if user provides an empty file.
    """
    with tempfile.NamedTemporaryFile(suffix='.csv') as temp:
        with pytest.raises(EmptyDataError):
            generate_trades(temp.name)


def test_rounding() -> None:
    """Test that the rounding function that we use throughout the codebase works as required by the problem.
    """
    assert np.round(0.555, 2) == 0.56
    assert np.round(0.554, 2) == 0.55
