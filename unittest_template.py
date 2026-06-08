#!/usr/bin/env python3

### UNIT TESTS
# - Run the tests by importing module and running the UnitTests() function
# - Or, execute the file and the main function at the end of the file executes the tests
# - Extract tests to separate files for a more traditional module setup

def UnitTests(verbosity=1):
  import unittest
  class ObjectTests(unittest.TestCase):
    def setUp(self):
      pass
    
    def tearDown(self):
      pass
    
    def test_init(self):
      o = object()
      self.assertIsNotNone(o)

  # Add all the cases for running in the suite to this collection      
  cases = (ObjectTests, )
  suite = unittest.TestSuite(
    [unittest.defaultTestLoader.loadTestsFromTestCase(t) for t in cases]
    )  
  unittest.TextTestRunner(verbosity=verbosity).run(suite)

      
      
if __name__ == "__main__":
  UnitTests()