#!/usr/bin/env python3

# xnumerate.py


def isXnumberable(o):
  try:
    _ = iter(o)
    if (type(o) == type('A')) and (len(o) < 2):
      return False
    return True
  except:
    return False

class xnumerate:
  def __init__(self, subject):
    _ = iter(subject) # raises TypeError of subject isn't iterable
    self._subject = subject
    
  def __iter__(self):
    self._iter_stack = [iter(self._subject)]
    self._index_stack = [0]
    return self
  def __next__(self):
    while len(self._iter_stack) > 0:
      top_iter = self._iter_stack[-1]
      try:
        n = next(top_iter)
        if isXnumberable(n):
          self._iter_stack.append(iter(n))
          self._index_stack.append(0)
          continue
        i = tuple(self._index_stack)
        if len(i) == 1:
          i = i[0]
        self._index_stack[-1] += 1
        return (i, n)
      except StopIteration:
        self._iter_stack.pop()
        self._index_stack.pop()
        if (len(self._index_stack) > 0):
          self._index_stack[-1] += 1
        continue
    raise StopIteration
  def sorted(self, key = lambda x: x):
    return sorted(self, key = lambda iv: key(iv[1]))


if __name__ == '__main__':
  """Unit Testing"""
  import unittest

  class XNumerateTests(unittest.TestCase):
    def test_xnumerateExists(self):
      x = xnumerate([6])
      self.assertEqual(type(x), xnumerate)

    def test_xnumerateIsIterable(self):
      _ = iter(xnumerate([6]))

    def test_xnumerateEmptySubject(self):
      i = iter(xnumerate([]))
      self.assertRaises(StopIteration, next, i)
    
    def test_xnumerateArgumentNotIterable(self): 
      self.assertRaises(TypeError, xnumerate, 7)

    def test_xnumerateOneItem(self):
      i = iter(xnumerate([6]))
      self.assertEqual(next(i), (0, 6))

    def test_xnumerate1x1(self):
      i = iter(xnumerate([[6]]))
      self.assertEqual(next(i), ((0, 0), 6))
      self.assertRaises(StopIteration, next, i)

    def test_xnumerate1x2(self):
      i = iter(xnumerate([[6, 7]]))
      self.assertEqual(next(i), ((0, 0), 6))
      self.assertEqual(next(i), ((0, 1), 7))
      self.assertRaises(StopIteration, next, i)

    def test_xnumerate2x2(self):
      i = iter(xnumerate([[6, 7], [9, 10]]))
      self.assertEqual(next(i), ((0, 0), 6))
      self.assertEqual(next(i), ((0, 1), 7))
      self.assertEqual(next(i), ((1, 0), 9))
      self.assertEqual(next(i), ((1, 1), 10))
      self.assertRaises(StopIteration, next, i)

    def test_xnumerateStringMixed(self):
      i = iter(xnumerate(['ab',['c', 'd']]))
      self.assertEqual(next(i), ((0, 0), 'a'))
      self.assertEqual(next(i), ((0, 1), 'b'))
      self.assertEqual(next(i), ((1, 0), 'c'))
      self.assertEqual(next(i), ((1, 1), 'd'))
      self.assertRaises(StopIteration, next, i)

    def test_xnumerateString2x2(self):
      i = iter(xnumerate([['a','b'],['y','z']]))
      self.assertEqual(next(i), ((0, 0), 'a'))
      self.assertEqual(next(i), ((0, 1), 'b'))
      self.assertEqual(next(i), ((1, 0), 'y'))
      self.assertEqual(next(i), ((1, 1), 'z'))

    def test_xnumerateSingleCharacter(self):
      i = iter(xnumerate('a'))
      self.assertEqual(next(i), (0, 'a'))

    def test_sortedOneItem(self):
      x = xnumerate([6])
      i = iter(x.sorted())
      self.assertEqual(next(i), (0, 6))

    def test_sortedTwoItems(self):
      x = xnumerate([7, 6])
      i = iter(x.sorted())
      self.assertEqual(next(i), (1, 6))

    def test_sortedWithKey(self):
      x = xnumerate((6, 7))
      i = iter(x.sorted(key = lambda x: -x))
      self.assertEqual(next(i), (1, 7))
      



  if __name__ == '__main__':
    unittest.main()
