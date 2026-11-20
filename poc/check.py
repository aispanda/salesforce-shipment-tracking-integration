"""Run the shipment prototype's offline acceptance checks."""

import unittest


def main():
    suite = unittest.defaultTestLoader.discover("tests")
    if suite.countTestCases() == 0:
        raise SystemExit("No shipment tests discovered")

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
