#!/usr/bin/env python3

# binary.py

import math


def setBits(a, b, start, count):
    first = a & ((1 << start) - 1)
    last = a >> (start+count)
    return first | (b << start) | (last << (start+count))

def getOnes(a):
    index = 0
    while (a > 0):
        if (a & 0x1):
            yield index
        index +=1
        a >>= 1

def getBits(a, n):
	while (n > 0):
		yield a & 0x1
		a >>= 1
		n -= 1

def getIndexedBits(a, n):
	i = 0;
	while (i < n):
		yield (i, a & 0x1)
		a >>= 1
		i += 1

def getBit(i, n):
    ii = i >> n
    return ii & 0x1

def setBit(i, n, b=True):
    ii = 1 << n
    if (b):
        return i | ii
    else:
        return i & (~ii)

def clearBit(i, n):
    return setBit(i, n, False)

def bitStr(a, n, separationWidth = None, separationCharacter=' '):
    s = ''.join([repr(num) for num in getBits(a,n)])[::-1]
    if separationWidth == None:
        return s
    t = ""
    while len(s) > 0:
        t = s[-separationWidth:] + separationCharacter + t
        s = s[:-separationWidth]
    if (t[-1]==separationCharacter):
        t = t[:-1]
    return t


# algorithm explained well at http://compprog.wordpress.com/2007/11/06/binary-numbers-counting-bits/
def countSparseOnes(i):
    count=0
    while i:
        count += 1
        i &= (i-1)
    return count

onesParcelSize = 16
onesParcelMap = [countSparseOnes(i) for i in range(1 << onesParcelSize)]
onesParcelMask = (1 << onesParcelSize) - 1

def countOnesByParcel(a):
    global onesParcelMap, onesParcelSize, onesParcelMask
    count = 0
    while a > 0:
        b = a & onesParcelMask
        count += onesParcelMap[a & onesParcelMask]
        a >>= onesParcelSize
    return count

countOnes=countOnesByParcel 


def bitDistance(a, b):
    return countOnesByParcel(a ^ b)

def highestOneIndex(a):
  if a==0:
    return -1
  return int(math.log(a)/math.log(2))

def invert(a, bitCount):
  return (~a) + (1 << bitCount)


class BitwiseData:
  """Encapsulates a binary value and its length"""
  def __init__(self, value=0, count=1):
    self.value = value
    minBits = 1 + highestOneIndex(value)
    if count < minBits:
      self.count = minBits
    else:
      self.count = count
  def copy(self):
    return BitwiseData(self.value, self.count)
  def __len__(self):
    return self.count
  def getBits(self):
    return self.value
  def countOnes(self):
    return countOnes(self.value)
  def __getitem__(self, n):
    return getBit(self.value, n)
  def __setitem__(self, n, b):
    self.value = setBit(self.value, n, b)
  def bitStr(self):
    return bitStr(self.value, self.count)
  def __ior__(self, other):
    self.value |= other.value
    return self
  def __or__(self, other):
    result = self.copy()
    result |= other
    return result
  def __ixor__(self, other):
    self.value ^= other.value
    return self
  def __xor__(self, other):
    result = self.copy()
    result ^= other
    return result
  def __iand__(self, other):
    self.value &= other.value
    return self
  def __and__(self, other):
    result= self.copy()
    result &= other
    return result
  def __invert__(self):
    result = self.copy()
    result.value = invert(result.value, result.count)
    return result
  def __eq__(self, other):
    return self.value == other.value and self.count == other.count
  def __ne__(self, other):
    return self.value != other.value or self.count != other.count
  def __hash__(self):
    return self.value % ((1<<31)-1)

"""Unit Testing"""
import unittest

class BitwiseDataTests(unittest.TestCase):
  def test_len(self):
    bitwiseData = BitwiseData(0,99)
    self.assertEqual(len(bitwiseData),99)

  def test_countOnes(self):
    bitwiseData = BitwiseData(0b10010110)
    self.assertEqual(bitwiseData.countOnes(), 4)

  def test_minCount(self):
    self.assertEqual(len(BitwiseData()),1)
    self.assertEqual(len(BitwiseData(1)),1)
    self.assertEqual(len(BitwiseData(0b10)),2)
    self.assertEqual(len(BitwiseData(0b10,3)),3)

  def test_getBit(self):
    bd = BitwiseData(count=4)
    self.assertEqual(bd[0],0)
    self.assertEqual(bd[1],0)
    self.assertEqual(bd[2],0)
    self.assertEqual(bd[3],0)
    bd = BitwiseData(0b1001,5)
    self.assertEqual(bd[0],1)
    self.assertEqual(bd[1],0)
    self.assertEqual(bd[2],0)
    self.assertEqual(bd[3],1)
    self.assertEqual(bd[4],0)

  def test_setBit(self):
    bd = BitwiseData(count=4)
    self.assertEqual(bd[2],0)
    bd[2] = 1
    self.assertEqual(bd[2],1)
    bd[2] = 0
    self.assertEqual(bd[2],0)

  def test_xor(self):
    bd1 = BitwiseData(0b1100)
    bd2 = BitwiseData(0b1010)
    bd1 ^= bd2
    self.assertEqual(bd1.getBits(), 0b0110)
    bd3 = bd2 ^ BitwiseData(0b0110)
    self.assertEqual(bd3.getBits(), 0b1100)

  def test_invert(self):
    bd = ~BitwiseData(0b1010,4)
    self.assertEqual(bd.getBits(), 0b0101)
    bd = ~BitwiseData(0,4)
    self.assertEqual(bd.getBits(), 0b1111)

  def test_copy(self):
    a = BitwiseData(0b11001010,8).copy()
    self.assertEqual(a.getBits(), 0b11001010)

  def test_and(self):
    bd1 = BitwiseData(0b1100)
    bd2 = BitwiseData(0b1010)
    bd1 &= bd2
    self.assertEqual(bd1.getBits(), 0b1000)
    bd3 = bd2 & BitwiseData(0b0110)
    self.assertEqual(bd3.getBits(), 0b0010)

  def test_or(self):
    bd1 = BitwiseData(0b1100)
    bd2 = BitwiseData(0b1010)
    bd1 |= bd2
    self.assertEqual(bd1.getBits(), 0b1110)
    bd1 = BitwiseData(0b0101,4)
    bd3 = bd1 | bd2
    self.assertEqual(bd3.getBits(), 0b1111)


