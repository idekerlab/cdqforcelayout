#!/usr/bin/env python

import os
import sys
import argparse
import traceback
import json
import logging
from contextlib import redirect_stdout

import ndex2
from qflayout import QFLayout


logger = logging.getLogger(__name__)


CY_VISUAL_PROPERTIES_ASPECT = 'cyVisualProperties'
"""
Name of aspect containing visual properties where
node size can be extracted
"""


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
    scalegroup = parser.add_mutually_exclusive_group()
    scalegroup.add_argument('--scale', type=float,
                            help='If set, overrides default and '
                                 'uniformly scales layout coordinates')
    scalegroup.add_argument('--fit_into', type=str,
                            help='If set, overrides default and uniformly '
                                 'adjusts layout coordinates to fit in'
                                 'bounding box passed in. Value should be a '
                                 'comma delimited list of floating point '
                                 'positions in format LEFT,TOP,RIGHT,BOTTOM '
                                 'ex: 0.0,0.0,500.0,600.0')
    return parser.parse_args(args)


def _get_node_size_from_cyvisual_properties(net_cx=None):
    """
    Gets node size from visual properties if it exists

    :param net_cx:
    :type net_cx: :py:class:`ndex2.nice_cx_network.NiceCXNetwork`
    :raises ValueError: If **net_cx** passed in is ``None``
    :return: Size of node as retrieved from cyVisualProperties
             aspect or None, if not found
    :rtype: float
    """
    if net_cx is None:
        raise ValueError('Network passed in cannot be None')

    v_props = net_cx.get_opaque_aspect(CY_VISUAL_PROPERTIES_ASPECT)
    if v_props is None:
        logger.debug('No ' + CY_VISUAL_PROPERTIES_ASPECT +
                     ' aspect found in network')
        return None
    for entry in v_props:
        if not entry['properties_of'] == 'nodes:default':
            continue

        return max(float(entry['properties']['NODE_WIDTH']),
                   float(entry['properties']['NODE_HEIGHT']),
                   float(entry['properties']['NODE_SIZE']))
    return None


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
            qfl = QFLayout.from_nicecx(net, theargs)
            new_layout = qfl.do_layout()
            # write value of cartesianLayout aspect to output stream
            json.dump(new_layout, out_stream)
        return 0
    except Exception as e:
        err_stream.write(str(e))
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
    
    NOTE: If neither, --scale or --fit_into are set then the layout
          coordinates are set to fit into the box where upper left
          corner is 0,0 and lower right corner is {DEF_BS},{DEF_BS} or 
          sqrt(size of node squared x number of nodes) where
          size of node is obtained from cyVisualProperties aspect
          or set to DEF_NS if not found. 
    """
    theargs = _parse_arguments(desc, args[1:])
    try:
        return run_layout(theargs, sys.stdout, sys.stderr)
    except Exception as e:
        sys.stderr.write('\n\nCaught exception: ' + str(e))
        traceback.print_exc()
        return 2


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
