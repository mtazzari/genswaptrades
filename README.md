# `genswaptrades`

[![image](https://github.com/mtazzari/genswaptrades/actions/workflows/tests.yml/badge.svg)](https://github.com/mtazzari/genswaptrades/actions/workflows/tests.yml)
[![License](https://img.shields.io/github/license/mtazzari/genswaptrades)](https://github.com/mtazzari/genswaptrades/blob/main/LICENSE)

A Python command-line utility that generates interest rate swap trades needed to achieve zero-sum notional value and cashflow.

This repository contains:

 - the code implementing the command-line utility;
 - documentation in the form of this README.md file;
 - unit tests quality assurance checks in the form of GitHub Actions workflows (see [here](https://github.com/mtazzari/genswaptrades/blob/main/.github/workflows)).

## Comment on the algorithm
Regarding the algorithm that I implemented to generate the 1 or 2 trades needed to achieve zero-sum notional value and cashflow. After reading the trades from file:
 
  - first, I check the rate that would be needed to complete the trades with just 1 trade. If that is outside 
    the [min_rate, max_rate] interval, which the problem set to [-0.1, 0.1] (with my utility they can be customized with `--min-rate` and `--max-rate`), then I opt for generating two trades.
  - if two trades are necessary, I compute their notional value and cashflow by solving this simple linear system of two equations in two unknowns:

$$Σ_i N_i + Trade1_N + Trade2_N = 0.  $$
for the notional value, and
$$Σ_i N_i * r_i + Trade1_N * Trade1_r + Trade2_N * Trade2_r = 0. $$
for the cashflow, where:
- $N_i$ is the notional value of the i-th trade provided in input, and $r_i$ is its rate.
- $Trade1_N$ and $Trade2_N$ are the notional values of the next two trades to be generated, and $Trade1_r$ and $Trade2_r$ are their rates.
- $Σ_i$ is a sum that runs over all the trades in input.

This system is made of two linear equations, and it has two unknowns: $Trade1_N$ and $Trade2_N$. I solved this system by hand in a minute:
$$Trade1_N = (Σ_i  N_i * Trade2_r - Σ_i  N_i * r_i) / (Trade1_r - Trade2_r) $$
$$Trade2_N = - Σ_i  N_i - Trade1_N $$
 
and I thus implemented this solution.

The algorithm has time complexity of O(N) as it needs to compute the sum of all notional (and cashflow) once. 

Theoretically, the algorithm has space complexity O(1), since it doesn't need to store all the trades in memory: it just needs to store the rolling sum of notional and cashflow as new trades are read from file. The present implementation in the tool has, however, space complexity O(N) because I opted to use `pandas` as a fast API for csv files, offering efficient rounding and sum operations. If the number of trades makes storage in memory challenging, then the algorithm can be easily converted to an O(1) implementation by dropping `pandas` and implementing a custom row-by-row reading.
  
## Installation
As easy as:

```bash
pip install git+https://github.com/mtazzari/genswaptrades.git
```

or, if you prefer to have the code locally, first clone the github repo and then install it with:

```bash
git clone https://github.com/mtazzari/genswaptrades.git
cd genswaptrades
pip install .
```

`genswaptrades` works in Python >= 3.7.

## Basic usage
Once installed, the Python command line utility `genswaptrades` can be called in the shell:
```bash
genswaptrades
```
The interface of the command line utility can be inspected with:
```bash
genswaptrades -h
```
which produces
```bash
$ genswaptrades -h
usage: use "genswaptrades --help" for more information

A Python command-line utility that, for a given list of trades, generates the 1 or 2 interest rate swap trades
needed to achieve zero-sum notional value and cashflow.

positional arguments:
  filename              [str] path to csv file containing the trades (columns: notional, rate).

options:
  -h, --help            show this help message and exit
  --run-tests           [bool] if True, generate interest swap trades for all the 3 provided test cases. Default: False
  --min-rate MIN_RATE   [float] minimum allowed rate. Default: -0.1.
  --max-rate MAX_RATE   [float] maximum allowed rate. Default: 0.1.
  --rates RATES RATES   [list of floats] if 2 trades are necessary to achieve zero-sum, the rates of these 2 trades.
                        The rates must be different and within [min_rate, max_rate] interval.
                        Example: `--rates 0.3 0.1`.
                        Default: None, which is equivalent to using rates [max_rate, max_rate - 0.1 * (max_rate - min_rate)]
  --log-level LOG_LEVEL
                        log level (debug:10, info:20, warning:30, error:40, critical:50). Default: 30
  -V, --version         show program's version number and exit
```
The filename `fname` is required for execution. 


## Usage
After installing `genswaptrades`, to quickly run the tool on the 3 test cases provided with the problem (i.e., trades1.csv, trades2.csv, trades3.csv), use the `--run-tests` argument:
```bash
$ genswaptrades --run-tests
/Users/mtazzari/repos/genswaptrades/genswaptrades/tests/assets/trades3.csv
Trade 5         -26409.60   0.10000000         -2640.96
Trade 6          26483.00   0.08000000          2118.64
/Users/mtazzari/repos/genswaptrades/genswaptrades/tests/assets/trades2.csv
Trade 6        3950072.95   0.00134147          5298.91
/Users/mtazzari/repos/genswaptrades/genswaptrades/tests/assets/trades1.csv
Trade 3        -545891.29   0.04889299        -26690.26
```

To run `genswaptrades` as per the test requirement, i.e. as  `genswaptrades <filename>`, just do: 
```bash
$ genswaptrades /Users/mtazzari/repos/genswaptrades/genswaptrades/tests/assets/trades3.csv
Trade 5         -26409.60   0.10000000         -2640.96
Trade 6          26483.00   0.08000000          2118.64
```
The output is just the list of new trade(s), with no header, as required.

By changing the log level, the user can obtain more informative output. By using `--log-level` argument, we can adjust the log level. Default is `WARNING` (30). By setting it to `INFO` (20), one gets:
```bash
$ genswaptrades /Users/mtazzari/repos/genswaptrades/genswaptrades/tests/assets/trades3.csv --log-level=20
2023-08-14 01:05:16,440 - genswaptrades.trades - INFO - Starting the trade generation for input file /Users/mtazzari/repos/genswaptrades/genswaptrades/tests/assets/trades3.csv: 4 trades found.
2023-08-14 01:05:16,440 - genswaptrades.trades - INFO - Initial notional_sum=-73.4 and cashflow_sum=522.32.
2023-08-14 01:05:16,440 - genswaptrades.trades - INFO - The rate of a single trade needed to achieve zero-sum is -7.11607629
2023-08-14 01:05:16,440 - genswaptrades.trades - INFO - The single-trade rate is outside of [-0.10000000,  0.10000000] interval: 2 trades are necessary.
2023-08-14 01:05:16,440 - genswaptrades.trades - INFO - Final notional_sum and cashflow_sum are expected to be both zero (i.e. < 0.01), got notional_sum=0.00            and cashflow_sum=0.00
2023-08-14 01:05:16,440 - genswaptrades.trades - INFO - Output columns, 1 row for each trade: Trade <trade no.>  <notional value>  <rate>  <cashflow>
Trade 5         -26409.60   0.10000000         -2640.96
Trade 6          26483.00   0.08000000          2118.64
```
The log level can be further lowered to `DEBUG` with  `--log-level 10`.

> **Note** :point_right: The calculations and the outputs adopt the rounding specified in the test: notional and cashflow are rounded to 2 decimal digits, the rate to 8 decimal digits.

## Python API
The utility `genswaptrades` makes it easy to generate interest rate swap trades via a clean command-line interface.

However, it also offers a neat Python API offered in the `genswaptrades.trades` module.
The `generate_trades()` function implements the trades generation and returns a list containing all the generated trades, for each trade a tuple containing (trade no., notional, rate, cashflow).

To generate trades a model and return the results as a string:
```py
from genswaptrades.trades import generate_trades

new_trades = generate_trades(fname="/path/to/filename.csv")
```
Example, with trades3.csv:
```py
In [1]: from genswaptrades.trades import generate_trades

In [2]: new_trades = generate_trades(fname="/Users/mtazzari/repos/genswaptrades/genswaptrades/tests/assets/trades3.csv")

In [3]: new_trades
Out[3]: [(5, -26409.6, 0.1, -2640.96), (6, 26483.0, 0.08, 2118.64)]
```
This allows users to generate trades programmatically, which is useful for data exploration, strategy evaluation, and further modelling.


## Comments & Outlook
The utility can be improved in many ways, depending on users' feedback.

In terms of architecture, here I've opted for a simple, procedural, approach, which allowed me to deliver quickly the desired functionality. With some interaction with the users, I would gather information on the preferred way of interacting with the tool, which would allow me to devise the correct implementation, depending on performance/versatility, flexibility, maintainability, expandability needs.

If, e.g., users will need a richer Python API, it would be natural to implement a simple `Trades` class which can be instantiated by providing a filename (csv or any generic tabular data file) or a pandas dataframe containing `notional, cashflow` columns or one (or more) `numpy` arrays. 

A `Trades` class could also implement some custom formatting of the output, which can be improved in many ways. For example, options could be added (i) to print all or the last N trades in the trades input file, (ii) to update the trades input file with the generate trades, (iii) to generate a new trades file with all the trades, including other columns (e.g., trade number, notional cashflow).


## Author
[Marco Tazzari](https://github.com/mtazzari)

## License
**genswaptrades** is free software licensed under the BSD-3 License. For more details see
the [LICENSE](https://github.com/mtazzari/genswaptrades/blob/main/LICENSE).



Copyright (c) 2023, Marco Tazzari
