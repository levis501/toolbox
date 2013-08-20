#!/usr/bin/env python3
"""Collection of math functions which are calculated recursively."""


__RMATH_FIBONACCI = {0:0, 1:1}
def fibonacci(n):
  if n in __RMATH_FIBONACCI.keys():
    return __RMATH_FIBONACCI[n]
  else:
    a = fibonacci(n-2)
    b = fibonacci(n-1)
    __RMATH_FIBONACCI[n]=a+b
    return a+b

__RMATH_FACTORIAL = {0:1}
def factorial(n):
  if n in __RMATH_FACTORIAL.keys():
    return __RMATH_FACTORIAL[n]
  else:
    result = n * factorial(n-1)
  __RMATH_FACTORIAL[n]=result
  return result

__RMATH_PERMUTATIONS = {}
def permutations(n,r):
  if n < 2:
    return 1
  if (n-r) < 2:
    return factorial(n)
  if (n,r) in __RMATH_PERMUTATIONS.keys():
    return __RMATH_PERMUTATIONS[(n,r)]
  p = permutations(n-1,r) * n // (n-r)
  __RMATH_PERMUTATIONS[(n,r)] = p
  return p

def combinations(n,r):
  return permutations(n,r) // factorial(r)
  

"""Unit Testing"""
import unittest

class Tests(unittest.TestCase):
  def test_fibonacci(self):
    self.assertEqual([fibonacci(n) for n in range(8)],[0, 1, 1, 2, 3, 5, 8, 13])
  def test_factorial(self):
    self.assertEqual([factorial(n) for n in range(8)],[1,1,2,6,24,120,720,5040])
  def test_combinations(self):
    self.assertEqual(combinations(3,2), 3)
    self.assertEqual(combinations(8,5), 56)
    self.assertEqual(combinations(6,4), 15)
  def test_permutations(self):
    self.assertEqual(permutations(3,2), 6)
    self.assertEqual(permutations(8,5), 6720)
    self.assertEqual(permutations(6,4), 360)

