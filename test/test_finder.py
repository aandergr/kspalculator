import unittest

from kspalculator.finder import Finder
from kspalculator.parts import RadialSize


class TestFinder(unittest.TestCase):
    def test_finder(self):
        """ check whether integration of kspalculator as a module works """
        f = Finder(1320, RadialSize.Small,
                [1170, 580, 580, 210, 700], [0.0, 3.3, 5.0, 0.0, 0.0], 5*[0.0],
                False, False, False, True, True)
        designs = f.find()
        self.assertEqual(len(designs), 7)