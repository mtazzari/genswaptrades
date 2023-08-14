#!/usr/bin/env python
# coding=utf-8
#
# command line interface (CLI) definition
#
import argparse
import logging
import os
from glob import glob

from genswaptrades import __version__
from genswaptrades.tests import TEST_ASSETS_DIR
from genswaptrades.trades import generate_trades, print_trades

# set up the root_logger
root_logger = logging.getLogger('')


def parse_args() -> dict:
    """Parse arguments from CLI.

    Returns:
        dict: the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="A Python command-line utility that, for a given list of trades, generates the 1 or 2 interest rate swap trades\n"
                    "needed to achieve zero-sum notional value and cashflow.",
        usage='use "%(prog)s --help" for more information',
        formatter_class=argparse.RawTextHelpFormatter  # for multi-line help text
    )
    parser.add_argument("filename",
                        action="store",
                        help="[str] path to csv file containing the trades (columns: notional, rate).\n",
                        type=str,
                        nargs="?",  # make the positional argument optional
                        default="")
    parser.add_argument("--run-tests", action="store_true",
                        help="[bool] if True, generate interest swap trades for all the 3 provided test cases. Default: False",
                        default=False)
    parser.add_argument("--min-rate", action="store",
                        type=float,
                        default=-0.1,
                        help="[float] minimum allowed rate. Default: -0.1."),
    parser.add_argument("--max-rate", action="store",
                        type=float,
                        default=0.1,
                        help="[float] maximum allowed rate. Default: 0.1."),
    parser.add_argument("--rates", action="store",
                        type=float, nargs=2,
                        help="[list of floats] if 2 trades are necessary to achieve zero-sum, the rates of these 2 trades.\n"
                             "The rates must be different and within [min_rate, max_rate] interval.\n"
                             "Example: `--rates 0.3 0.1`.\n"
                             "Default: None, which is equivalent to using rates [max_rate, max_rate - 0.1 * (max_rate - min_rate)]")
    parser.add_argument('--log-level',
                        help='[int] log level (debug:10, info:20, warning:30, error:40, critical:50). Default: 30\n'
                             "Note: `--log-level` has no effect if `--debug` is passed",
                        default=30, type=int)
    parser.add_argument("-d", "--debug", action="store_true",
                        help="[bool] if True, log level is set to debug: 10. Equivalent to `--log-level=10`.\n"
                             "Note: `--log-level` has no effect if `--debug` is passed. Default: False",
                        default=False)
    parser.add_argument("-V", "--version",
                        action="version",
                        version='{}'.format(__version__)
                        )

    args = vars(parser.parse_args())  # convert to dict for ease of use

    return args


def validate_args(args: dict) -> None:
    """Validate CLI arguments.

    Args:
        args (dict): the CLI arguments.

    Raises:
        ValueError: if the args['filename'] is not a csv file.
    """
    filename, ext = os.path.splitext(args['filename'])

    if filename and ext.upper() != '.CSV':
        raise ValueError(f"Expecting the filename with 'CSV' or 'csv' extension, got '{ext}'.")


def main() -> None:
    """
    Main function, called through the shell entrypoint.
    Parse the arguments, read the input csv filename, and generate the trades.
    """
    # parse and validate the arguments
    args = parse_args()
    validate_args(args)

    # setup logger
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)
    logging_level = args.pop('log_level') if not args['debug'] else 10
    root_logger.setLevel(logging_level)

    # run the trade generator
    root_logger.debug("command-line arguments: {}".format(args))
    if args['run_tests']:
        test_files = sorted(glob(os.path.join(TEST_ASSETS_DIR, "trades*.csv")))
        root_logger.info("The following test files were found:\n{}\n".format("\n".join(test_files)))
        root_logger.info("Starting the trade generation:")
        for test_file in test_files:
            print(test_file)
            print_trades(
                generate_trades(
                    test_file,
                    min_rate=args['min_rate'],
                    max_rate=args['max_rate'],
                    additional_trade_rates=args.get('rates')
                )
            )

        exit(0)

    # generate and print the trades
    print_trades(
        generate_trades(
            args['filename'],
            min_rate=args['min_rate'],
            max_rate=args['max_rate'],
            additional_trade_rates=args.get('rates')
        )
    )


if __name__ == "__main__":
    main()
