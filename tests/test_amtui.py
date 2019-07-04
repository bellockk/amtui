#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `amtui` package."""


import unittest
from click.testing import CliRunner

from amtui import cli


class TestAmtui(unittest.TestCase):
    """Tests for `amtui` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        help_result = runner.invoke(cli.gui, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
