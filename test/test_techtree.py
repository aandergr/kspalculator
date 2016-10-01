import doctest

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite("kspalculator.techtree"))
    return tests