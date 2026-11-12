"""Intentional failing test for the isolated CI negative control."""

import unittest


class CINegativeControl(unittest.TestCase):
    def test_intentional_failure(self):
        self.fail("Intentional CI negative control")
