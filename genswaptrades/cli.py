#!/usr/bin/env python
# coding=utf-8
#
# command line interface (CLI) definition
#
import argparse
import os
from glob import glob

from genswaptrades import __version__
from genswaptrades.tests import TEST_ASSETS_DIR
from genswaptrades.trades import generate_trades, print_trades


def parse_args() -> dict:
    """Parse arguments from CLI.


    Returns:
        dict: the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="A Python command-line utility that computes premiums for specific exposure models.",
        usage='use "%(prog)s --help" for more information',
        formatter_class=argparse.RawTextHelpFormatter  # for multi-line help text
    )
    parser.add_argument(action="store",
                        help="[str] path to JSON file containing definition of model, parameters, and outputs.",
                        type=str,
                        default="",
                        dest="filename")
    parser.add_argument("--run-tests", action="store_true",
                        help="[bool] if True, generate interest swap trades for all the test cases. Default: False",
                        default=False)
    parser.add_argument("-d", "--debug", action="store_true",
                        help="[bool] if True, the full model_data dict with results is printed to terminal. Default: False",
                        default=False)
    parser.add_argument("--rates", action="store",
                        type=float, nargs=2,
                        help="[list of floats] terminal. Default: False",
                        )
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
    _, ext = os.path.splitext(args['filename'])

    if ext.upper() != '.CSV':
        raise ValueError(f"Expecting the filename with 'CSV' or 'csv' extension, got '{ext}'.")


def main() -> None:
    """
    Main function, called through the shell entrypoint.
    Parse the arguments, read the input csv filename, and generate the trades.
    """
    args = parse_args()

    validate_args(args)

    if args['run_tests']:
        test_files = glob(os.path.join(TEST_ASSETS_DIR, "trades*.csv"))

        for test_file in test_files:
            print(test_file)
            print_trades(generate_trades(test_file))

    # generate and print the trades
    print_trades(generate_trades(args['filename'], additional_trade_rates=args.get('rates')))


if __name__ == "__main__":
    main()
