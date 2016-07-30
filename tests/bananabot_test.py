#!/usr/bin/env python3
import unittest
try:
    from unittest import mock
except ImportError:  # For Python versions earlier than 3.3
    import mock


class TestBananaBot(unittest.TestCase):
    pass

if __name__ == "__main__":
    unittest.main()
