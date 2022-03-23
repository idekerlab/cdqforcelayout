#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_cdqforcelayout
----------------------------------

Tests for `cdqforcelayout` module.
"""

import os
import sys
import unittest
import io
import tempfile
import shutil
import json
from cdqforcelayout import cdqforcelayoutcmd


class TestCdqforceLayout(unittest.TestCase):

    TEST_DIR = os.path.dirname(__file__)

    HUNDRED_NODE_DIR = os.path.join(TEST_DIR, 'data',
                                    'test_nectin_adhesion')

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_args_all_defaults(self):
        myargs = ['inputarg']
        res = cdqforcelayoutcmd._parse_arguments('desc', myargs)
        self.assertEqual('inputarg', res.input)
        self.assertEqual('auto', res.layout)

    def test_runlayout_input_is_not_a_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            args = cdqforcelayoutcmd._parse_arguments('desc',
                                                      [os.path.join(temp_dir,
                                                                    'input')])
            o_stream = io.StringIO()
            e_stream = io.StringIO()
            res = cdqforcelayoutcmd.run_layout(args, out_stream=o_stream,
                                               err_stream=e_stream)
            self.assertEqual(3, res)

        finally:
            shutil.rmtree(temp_dir)

    def test_runlayout_input_is_not_an_empty_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            input_file = os.path.join(temp_dir, 'input')
            open(input_file, 'a').close()
            args = cdqforcelayoutcmd._parse_arguments('desc',
                                                      [input_file])
            o_stream = io.StringIO()
            e_stream = io.StringIO()
            res = cdqforcelayoutcmd.run_layout(args, out_stream=o_stream,
                                               err_stream=e_stream)
            self.assertEqual(4, res)
        finally:
            shutil.rmtree(temp_dir)

    def test_runlayout_on_test_nectin_adhesion(self):
        temp_dir = tempfile.mkdtemp()
        try:
            nectin = os.path.join(os.path.dirname(__file__), 'data',
                                  'test_nectin_adhesion.cx')

            args = cdqforcelayoutcmd._parse_arguments('desc',
                                                      [nectin])
            o_stream = io.StringIO()
            e_stream = io.StringIO()
            res = cdqforcelayoutcmd.run_layout(args, out_stream=o_stream,
                                               err_stream=e_stream)
            self.assertEqual('', e_stream.getvalue())
            self.assertEqual(0, res)
            cart_layout = json.loads(o_stream.getvalue())
            self.assertTrue(isinstance(cart_layout, list))
            self.assertEqual(33, len(cart_layout))
            for entry in cart_layout:
                self.assertTrue('node' in entry)
                self.assertTrue('x' in entry)
                self.assertTrue('y' in entry)

        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    sys.exit(unittest.main())
