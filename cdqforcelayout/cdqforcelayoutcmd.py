#!/usr/bin/env python

import os
import sys
import argparse
import traceback
import json
import logging
from contextlib import redirect_stdout

import ndex2
from cdqforcelayout import qflayout


logger = logging.getLogger('cdqforcelayout.cdqforcelayoutcmd')


LOG_FORMAT = "%(asctime)-15s %(levelname)s %(relativeCreated)dms " \
             "%(filename)s::%(funcName)s():%(lineno)d %(message)s"


class Formatter(argparse.ArgumentDefaultsHelpFormatter,
                argparse.RawDescriptionHelpFormatter):
    pass


def _parse_arguments(desc, args):
    """
    Parses command line arguments

    :param desc: Description shown when -h is passed on
                 command line
    :type desc: str
    :param args: Arguments from command line
    :type args: list
    :return: Argument Parser
    :rtype: :py:class:`argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=Formatter)
    parser.add_argument('input',
                        help='CX file')
    parser.add_argument('--layout', default='auto',
                        choices=['auto'],
                        help='Layout algorithm to use. '
                             'so far, there is only the default'
                            )
    parser.add_argument('--rounds', default=10, type=int,
                        help='Number of layout iterations')
    parser.add_argument('--sparsity', default=30, type=int,
                        help='TODO, please fill out')
    parser.add_argument('--a_radius', default=40, type=int,
                        help='TODO, please fill out')
    parser.add_argument('--r_radius', default=10, type=int,
                        help='TODO, please fill out')
    parser.add_argument('--r_scale', default=7, type=int,
                        help='TODO, please fill out')
    parser.add_argument('--a_scale', default=5, type=int,
                        help='TODO, please fill out')
    parser.add_argument('--center_attractor_scale', default=0.02, type=float,
                        help='TODO, please fill out')
    parser.add_argument('--initialize_coordinates', choices=['center', 'random', 'spiral'],
                        default='spiral',
                        help='TODO, please fill out')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='Increases verbosity of logger to standard '
                             'error for log messages in this module and '
                             '. Messages are '
                             'output at these python logging levels '
                             '-v = ERROR, -vv = WARNING, -vvv = INFO, '
                             '-vvvv = DEBUG, -vvvvv = NOTSET (default is to '
                             'log CRITICAL)')
    parser.add_argument('--logconf', default=None,
                        help='Path to python logging configuration file in '
                             'format consumable by fileConfig. See '
                             'https://docs.python.org/3/library/logging.html '
                             'for more information. '
                             'Setting this overrides -v|--verbose parameter '
                             'which uses default logger. (default None)')
    return parser.parse_args(args)


def _setup_logging(args):
    """
    Sets up logging based on parsed command line arguments.
    If args.logconf is set use that configuration otherwise look
    at args.verbose and set logging for this module and the one
    in ndexutil specified by TSV2NICECXMODULE constant
    :param args: parsed command line arguments from argparse
    :raises AttributeError: If args is None or args.logconf is None
    :return: None
    """

    if args.logconf is None:
        level = (50 - (10 * args.verbose))
        logging.basicConfig(format=LOG_FORMAT,
                            level=level)
        logger.setLevel(level)
        return

    # logconf was set use that file
    logging.config.fileConfig(args.logconf,
                              disable_existing_loggers=False)


def run_layout(theargs, out_stream=sys.stdout,
               err_stream=sys.stderr):
    """
    Runs the QForce layout

    :param theargs: Holds attributes from argparse
    :type theargs: `:py:class:`argparse.Namespace`
    :param out_stream: stream for standard output
    :type out_stream: file like object
    :param err_stream: stream for standard error output
    :type err_stream: file like object
    :return: 0 upon success otherwise error
    :rtype: int
    """

    if theargs.input is None or not os.path.isfile(theargs.input):
        err_stream.write(str(theargs.input) + ' is not a file')
        return 3

    if os.path.getsize(theargs.input) == 0:
        err_stream.write(str(theargs.input) + ' is an empty file')
        return 4

    try:
        with redirect_stdout(sys.stderr):
            net = ndex2.create_nice_cx_from_file(theargs.input)
            qfl = qflayout.QFLayout.from_nicecx(net,
                                                initialize_coordinates=theargs.initialize_coordinates,
                                                sparsity=theargs.sparsity,
                                                a_radius=theargs.a_radius,
                                                r_scale=theargs.r_scale,
                                                a_scale=theargs.a_scale,
                                                center_attractor_scale=theargs.center_attractor_scale)
            new_layout = qfl.do_layout(rounds=theargs.rounds)
            # write value of cartesianLayout aspect to output stream
            logger.debug(str(new_layout))
            json.dump(new_layout, out_stream)
        return 0
    except Exception as e:
        err_stream.write('Caught exception: ' + str(e) + '\n')
        traceback.print_exc()
        return 5
    finally:
        err_stream.flush()
        out_stream.flush()


def main(args):
    """
    Main entry point for program
    :param args: command line arguments usually :py:const:`sys.argv`
    :return: 0 for success otherwise failure
    :rtype: int
    """
    desc = """
    Runs qforce layout on command line, sending cartesianLayout aspect
    to standard out.
    """
    theargs = _parse_arguments(desc, args[1:])
    try:
        _setup_logging(theargs)
        return run_layout(theargs, sys.stdout, sys.stderr)
    except Exception as e:
        sys.stderr.write('\n\nCaught exception: ' + str(e))
        traceback.print_exc()
        return 2


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
