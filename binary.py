#!/usr/bin/env python3

# binary.py

import math
import random
import functools

def setBits(dest, bits, start, count):
    hi = dest & ((1 << start) - 1)
    lo = dest >> (start+count)
    return hi | (bits << start) | (lo << (start+count))

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
  i = 0
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
    if separationWidth is None:
        return s
    t = ""
    offset = -1 * separationWidth
    while len(s) > 0:
        t = s[offset:] + separationCharacter + t
        s = s[:offset]
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


_onesParcelSize = 16
_onesParcelMap = [countSparseOnes(i) for i in range(1 << _onesParcelSize)]
_onesParcelMask = (1 << _onesParcelSize) - 1
def countOnesByParcel(a):
    global _onesParcelMap, _onesParcelSize, _onesParcelMask
    count = 0
    while a > 0:
        b = a & _onesParcelMask
        count += _onesParcelMap[b]
        a >>= _onesParcelSize
    return count

_countOnesCache = {}
def countOnes(a, useCache=False):
  global _countOnesCache
  if useCache:
    try:
      return _countOnesCache[a]
    except KeyError:
      count = countOnesByParcel(a)
      _countOnesCache[a] = count
      return count
  return countOnesByParcel(a)

def countZeros(a,n,useCache=False):
  return n-countOnes(a,useCache)

def bitDistance(a, b):
    return countOnesByParcel(a ^ b)

def highestOneIndexSlow(a):
  result = -1
  while a > 0:
    result += 1
    a >>= 1
  return result

def highestOneIndex(a):
  if a==0:
    return -1
  n64 = 0
  x = a >> 64
  while x > 0:
    n64 += 1
    x >>= 64
  n = 64 * n64
  x = a >> (n+1)
  while x > 0:
    n += 1
    x >>= 1
  return n

def invert(a, bitCount):
  return (~a) + (1 << bitCount)

def rshift(a, bitCount, n):
  n = n % bitCount
  if n==0: return a
  loBits = ((1<<n)-1) & a
  a >>= n
  a = setBits(a, loBits, bitCount-n, n)
  return a
  
def lshift(a, bitCount, n):
  return rshift(a, bitCount, bitCount-n)

def fromList(bitList):
  value = 0
  for (i,bit) in enumerate(bitList):
    value += (int(bit) << i)
  return value

class BitwiseData:
  """Encapsulates a binary value and its length"""
  DEFAULT_STRING_SEPARATION = None
  def __init__(self, count=None, value=0, msb_first=False):
    self.value = value
    minBits = 1 + highestOneIndex(value)
    if (count is None):
      self.count = max(minBits,1)
    elif count < minBits:
      raise ValueError("count parameter %d is insufficeint to hold value with hi bit %d" % (count, minBits))
    else:
      self.count = count
    if msb_first:
      self.value = self.reversed().value
    
  def copy(self):
    return BitwiseData(self.count, self.value)
  def randomize(self, rng=random.getrandbits):
    self.value = rng(self.count)
    return self
  def __len__(self):
    return self.count
  def setBits(self, bits, start=0, count=None):
    if count is None:
      count = self.count-start
    self.value = setBits(self.value, bits, start, count)
    return self
  def setValue(self, value):
    self.value = value
  def countOnes(self, useCache=False):
    return countOnes(self.value, useCache)
  def countZeros(self, useCache=False):
    return countZeros(self.value, self.count, useCache)
  def __getitem__(self, key):
    if isinstance(key, slice):
      s = list(self)[key]
      if len(s) < 1:
        raise ValueError("Cannot slice BinaryData to zero bits (%s)" % key)
      return BitwiseData.createFromList(s)
    return getBit(self.value, key)
  def __setitem__(self, n, b):
    self.value = setBit(self.value, n, b)
  def __delitem__(self, n):
    highBits = ((self.value >> (n+1)) << n) 
    if (n > 0):
      lowBits = self.value & invert(0, n-1)
    else:
      lowBits = 0
    self.value = highBits | lowBits
    self.count -= 1
  def flip(self, b):
    self.value ^= (1 << b)
  def bitStr(self, separationWidth = None, separationCharacter=' '):
    if separationWidth == None:
      separationWidth = BitwiseData.DEFAULT_STRING_SEPARATION
    return bitStr(self.value, self.count, separationWidth, separationCharacter)
  def __ior__(self, other):
    self.value |= other.value if (type(other)==BitwiseData) else other
    return self
  def __or__(self, other):
    result = self.copy()
    result |= other
    return result
  def __ixor__(self, other):
    self.value ^= other.value if (type(other)==BitwiseData) else other
    return self
  def __xor__(self, other):
    result = self.copy()
    result ^= other
    return result
  def __iand__(self, other):
    self.value &= other.value if (type(other)==BitwiseData) else other
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
    if other is None:
      return False
    if (type(other) == BitwiseData):
      return self.value == other.value and self.count == other.count
    else:
      return self.value == other
  def __ne__(self, other):
    if other is None:
      return True
    if (type(other) == BitwiseData):
      return self.value != other.value or self.count != other.count
    else:
      return self.value != other
  def __hash__(self):
    return self.value % ((1<<31)-1)
  def __repr__(self):
    return "0b" + self.__str__()
  def __str__(self):
    return self.bitStr()
  def __iter__(self):
    value = self.value
    count = self.count
    while count > 0:
      yield value & 0x1
      value >>= 1
      count -= 1
    return
  def ones(self):
    value = self.value
    index = 0
    while index < self.count:
      if value & 0x1:
        yield index
      value >>= 1
      index += 1
    return
  def zeros(self):
    return (~self).ones()
  def nthOne(self, n, onesCount=None):
    if onesCount is None:
      onesCount = self.countOnes()
    g = self.ones()
    while n >= 0:
      i = next(g)
      n -= 1
    return i
  def nthZero(self, n, zeroCount=None):
    if zeroCount is None:
      zeroCount = self.countZeros()
    g = self.zeros()
    while n >= 0:
      i = next(g)
      n -= 1
    return i    
  def increaseCapacity(self, increaseAmount):
    self.count += increaseAmount
    self.setZeros(self.count - increaseAmount, increaseAmount)
  def bitDistance(self, other):
    return bitDistance(self.value, other.value if type(other)==BitwiseData else other)
  def setAllZeros(self):
    self.value = 0
  def setAllOnes(self):
    self.value = invert(0, self.count)
  def setZeros(self, start, count):
    self.setBits(0, start, count)
  def setOnes(self, start, count):
    self.setBits(invert(0, count), start, count)
  def getIndexedBits(self):
    a = self.value
    n = self.count
    i = 0
    while (i < n):
      yield (i, a & 0x1)
      a >>= 1
      i += 1
    return
  def substr(self, start, count):
    return BitwiseData(count,(self.value >> start) & ((1<<count)-1))
  def rshift(self, n):
    self.value = rshift(self.value, self.count, n)
  def lshift(self, n):
    self.value = lshift(self.value, self.count, n)
  def correlate(self, other):
    return self.count - 2 * self.bitDistance(other)
  def reversed(self):
    return BitwiseData.convert(reversed(self))
  def append(self, appendage):
    appendage = BitwiseData.convert(appendage)
    original_count = self.count
    self.increaseCapacity(appendage.count)
    self.setBits(appendage.value, original_count)

  @staticmethod
  def concat(a, b=None):
    if (b == None):
      c = functools.reduce(BitwiseData.concat, a)
    else:
      c = a.copy()
      c.append(b)
    return c

  @staticmethod
  def createFromList(bitList):
    return BitwiseData(len(bitList), fromList(bitList))

  @staticmethod
  def convert(origin, count=None):
    if type(origin) == list:
      return BitwiseData.createFromList(origin)
    if type(origin) == BitwiseData:
      return origin
    if type(origin) == int:
      return BitwiseData(count, origin)
    try:
      iter(origin)
      return BitwiseData.createFromList(list(origin))
    except TypeError:
      raise NotImplementedError(f'No conversion exists for type {type(origin)}')

if __name__ == '__main__':
  """Unit Testing"""
  import unittest

  class BinaryTests(unittest.TestCase):
    def test_highestOneIndex(self):
      self.assertEqual(highestOneIndex(0), -1)
      self.assertEqual(highestOneIndex(0xFF), 7)
      self.assertEqual(highestOneIndex(1 << 63), 63)
      self.assertEqual(highestOneIndex((1 << 64)-1), 63)
      self.assertEqual(highestOneIndex(1 << 128), 128)
      self.assertEqual(highestOneIndex(1 << 1023), 1023)
      self.assertEqual(highestOneIndex((1 << 1024)-1), 1023)

  class BitwiseDataTests(unittest.TestCase):
    def test_len(self):
      bitwiseData = BitwiseData(99, 0)
      self.assertEqual(len(bitwiseData), 99)

    def test_countOnes(self):
      bitwiseData = BitwiseData(8, 0b10010110)
      self.assertEqual(bitwiseData.countOnes(), 4)

    def test_countZeros(self):
      bitwiseData = BitwiseData(8, 0b10010110)
      self.assertEqual(bitwiseData.countZeros(), 4)

    def test_msbFirst(self):
      a = BitwiseData(8, 0b10010110, msb_first=True)
      b = BitwiseData(8, 0b01101001, msb_first=False)
      self.assertEqual(a, b)

      
    def test_nthOne(self):
      bitwiseData = BitwiseData(8, 0b10010110)
      self.assertEqual(bitwiseData.nthOne(0),1)
      self.assertEqual(bitwiseData.nthOne(1),2)
      self.assertEqual(bitwiseData.nthOne(2),4)
      self.assertEqual(bitwiseData.nthOne(3),7)      

    def test_nthZero(self):
      bitwiseData = BitwiseData(8, 0b10010110)
      self.assertEqual(bitwiseData.nthZero(0),0)
      self.assertEqual(bitwiseData.nthZero(1),3)
      self.assertEqual(bitwiseData.nthZero(2),5)
      self.assertEqual(bitwiseData.nthZero(3),6)      

    def test_minCount(self):
      self.assertEqual(len(BitwiseData()), 1)
      self.assertEqual(len(BitwiseData(value=1)), 1)
      self.assertEqual(len(BitwiseData(value=0b10)), 2)
      self.assertEqual(len(BitwiseData(3, 0b10)), 3)

    def test_getBit(self):
      bd = BitwiseData(4)
      self.assertEqual(bd[0], 0)
      self.assertEqual(bd[1], 0)
      self.assertEqual(bd[2], 0)
      self.assertEqual(bd[3], 0)
      bd = BitwiseData(5, 0b1001)
      self.assertEqual(bd[0], 1)
      self.assertEqual(bd[1], 0)
      self.assertEqual(bd[2], 0)
      self.assertEqual(bd[3], 1)
      self.assertEqual(bd[4], 0)

    def test_setBit(self):
      bd = BitwiseData(4)
      self.assertEqual(bd[2], 0)
      bd[2] = 1
      self.assertEqual(bd[2], 1)
      bd[2] = 0
      self.assertEqual(bd[2], 0)

    def test_setBits(self):
      bd = BitwiseData(8, 0b11010111)
      bd.setBits(0b1010, 2, 4)
      self.assertEqual(bd, 0b11101011)

    def test_equal(self):
      bd = BitwiseData(8, 0b01010111)
      self.assertTrue(bd == bd)
      self.assertFalse(bd == None)
      self.assertEqual(bd, BitwiseData(8, 0b01010111))
      self.assertEqual(bd, 0b01010111)

    def test_xor(self):
      bd1 = BitwiseData(4, 0b1100)
      bd2 = BitwiseData(4, 0b1010)
      bd1 ^= bd2
      self.assertEqual(bd1, 0b0110)
      bd3 = bd2 ^ BitwiseData(4, 0b0110)
      self.assertEqual(bd3, 0b1100)
      bd4 = bd3 ^ 0b1001
      self.assertEqual(bd4, 0b0101)

    def test_invert(self):
      bd = ~BitwiseData(4, 0b1010)
      self.assertEqual(bd, 0b0101)
      bd = ~BitwiseData(4, 0)
      self.assertEqual(bd, 0b1111)

    def test_copy(self):
      a = BitwiseData(8, 0b11001010).copy()
      self.assertEqual(a, 0b11001010)

    def test_and(self):
      bd1 = BitwiseData(4, 0b1100)
      bd2 = BitwiseData(4, 0b1010)
      bd1 &= bd2
      self.assertEqual(bd1, 0b1000)
      bd3 = bd2 & BitwiseData(4, 0b0110)
      self.assertEqual(bd3, 0b0010)

    def test_or(self):
      bd1 = BitwiseData(4, 0b1100)
      bd2 = BitwiseData(4, 0b1010)
      bd1 |= bd2
      self.assertEqual(bd1, 0b1110)
      bd1 = BitwiseData(4, 0b0101)
      bd3 = bd1 | bd2
      self.assertEqual(bd3, 0b1111)
      bd4 = bd1 | 0b1010
      self.assertEqual(bd4, 0b1111)

    def test_iter(self):
      a = BitwiseData(8, 0b11001010)
      b = [bit for bit in a]
      self.assertEqual(b, [0, 1, 0, 1, 0, 0, 1, 1])

    def test_ones(self):
      a = BitwiseData(8, 0b11001010)
      self.assertEqual([one for one in a.ones()], [1, 3, 6, 7])

    def test_zeros(self):
      a = BitwiseData(8, 0b11001010)
      self.assertEqual([zero for zero in a.zeros()], [0, 2, 4, 5])

    def test_increaseCapacity(self):
      a = BitwiseData(8, 0b11001010)
      self.assertEqual(len(a), 8)
      a.increaseCapacity(1)
      self.assertEqual(len(a), 9)
      a.increaseCapacity(10)
      self.assertEqual(len(a), 19)

    def test_bitDistance(self):
      a = BitwiseData(8, 0b10100101)
      b = BitwiseData(8, 0b00001111)
      self.assertEqual(a.bitDistance(b), 4)
      c = BitwiseData(4, 0b1111)
      self.assertEqual(b.bitDistance(c), 0)

    def test_setAll(self):
      a = BitwiseData(8, 0b10100101)
      self.assertEqual(a.countOnes(), 4)
      a.setAllZeros()
      self.assertEqual(a.countOnes(), 0)
      b = BitwiseData(8, 0b00001111)
      self.assertEqual(b.countOnes(), 4)
      b.setAllOnes()
      self.assertEqual(b.countOnes(), 8)

    def test_getIndexedBits(self):
      a = BitwiseData(8, 0b10100111)
      l = [1, 1, 1, 0, 0, 1, 0, 1]
      for (i, b) in a.getIndexedBits():
        self.assertEqual(b, l[i])

    def test_setZeros(self):
      a = BitwiseData(8, 0b10100111)
      b = BitwiseData(8, 0b10000011)
      a.setZeros(2, 5)
      self.assertEqual(a, b)

    def test_setOnes(self):
      a = BitwiseData(8, 0b10100111)
      b = BitwiseData(8, 0b11111111)
      a.setOnes(2, 5)
      self.assertEqual(a, b)

    def test_substr(self):
      a = BitwiseData(8, 0b10100111)
      self.assertEqual(a.substr(0, 3), BitwiseData(3, 0b111))
      self.assertEqual(a.substr(1, 4), BitwiseData(4, 0b0011))
      self.assertEqual(a.substr(2, 5), BitwiseData(5, 0b01001))
      self.assertEqual(a.substr(3, 5), BitwiseData(5, 0b10100))

    def test_delitem(self):
      a = BitwiseData(8, 0b10100111)
      del a[4]
      self.assertEqual(a, BitwiseData(7, 0b1010111))
      del a[4]
      self.assertEqual(a, BitwiseData(6, 0b100111))
      del a[0]
      self.assertEqual(a, BitwiseData(5, 0b10011))
      del a[4]
      self.assertEqual(a, BitwiseData(4, 0b0011))
      
    def test_rshift(self):
      a = BitwiseData(5, 0b11010)
      a.rshift(1)
      self.assertEqual(a, BitwiseData(5, 0b01101))
      a.rshift(2)
      self.assertEqual(a, BitwiseData(5, 0b01011))
      a.rshift(3)
      self.assertEqual(a, BitwiseData(5, 0b01101))
      a.rshift(4)
      self.assertEqual(a, BitwiseData(5, 0b11010))
      a.rshift(5)
      self.assertEqual(a, BitwiseData(5, 0b11010))
      a.rshift(6)
      self.assertEqual(a, BitwiseData(5, 0b01101))
      
    def test_lshift(self):
      a = BitwiseData(5, 0b11010)
      a.lshift(1)
      self.assertEqual(a, BitwiseData(5, 0b10101))
      a.lshift(2)
      self.assertEqual(a, BitwiseData(5, 0b10110))
      a.lshift(3)
      self.assertEqual(a, BitwiseData(5, 0b10101))
      a.lshift(4)
      self.assertEqual(a, BitwiseData(5, 0b11010))
      a.lshift(5)
      self.assertEqual(a, BitwiseData(5, 0b11010))
      a.lshift(6)
      self.assertEqual(a, BitwiseData(5, 0b10101))

    def test_fromList(self):
      a = BitwiseData.createFromList([0])
      self.assertEqual(a, BitwiseData(1, 0b0))
      a = BitwiseData.createFromList([1])
      self.assertEqual(a, BitwiseData(1, 0b1))
      a = BitwiseData.createFromList([1,0,0,1,0,1,1,0])
      self.assertEqual(a, BitwiseData(8, 0b01101001))

    def test_concat(self):
      a = BitwiseData(5, 0b11010)
      b = BitwiseData(3, 0b010)
      c = BitwiseData.concat([a, b])
      self.assertEqual(c, BitwiseData(8, 0b01011010))
      d = BitwiseData.concat(a, b)
      self.assertEqual(d, BitwiseData(8, 0b01011010))
      e = BitwiseData(9, 0b1)
      f = BitwiseData.concat([a, b, e])
      self.assertEqual(f, BitwiseData(17, 0b101011010));

    def test_append(self):
      a = BitwiseData(5, 0b11010)
      b = BitwiseData(3, 0b010)
      a.append(b)
      self.assertEqual(a, BitwiseData(8, 0b01011010))
      a.append(1)
      self.assertEqual(a, BitwiseData(9, 0b101011010))
      a.append(0)
      self.assertEqual(a, BitwiseData(10, 0b0101011010))

    def test_correlate(self):
      a = BitwiseData(5, 0b11010)
      b = BitwiseData(5, 0b10101)
      self.assertEqual(a.correlate(b), -3)
      self.assertEqual(b.correlate(a), -3)
      c = BitwiseData(8, 0b11110000)
      d = BitwiseData(8, 0b11100001)
      self.assertEqual(c.correlate(d), 4)
      self.assertEqual(d.correlate(c), 4)

    def test_convert(self):
      a = BitwiseData.convert(0b01011, 5)
      self.assertEqual(a, BitwiseData(5, 0b01011))
      b = BitwiseData.convert([1, 1, 0, 1, 0])
      self.assertEqual(b, BitwiseData(5, 0b01011))
      c = BitwiseData(5, 0b01011)
      self.assertEqual(c, BitwiseData(5, 0b01011))

    def test_slice(self):
      a = BitwiseData(8, 0b10110100)
      self.assertEqual(a[:], 0b10110100)
      self.assertEqual(a[0:], 0b10110100)
      self.assertEqual(a[1:], 0b1011010)
      self.assertEqual(a[::-1], 0b00101101)
      self.assertEqual(a[5:3:-1], 0b11)

    def mock_rng8(self, bitsRequested):
      self.assertEqual(bitsRequested, 8, "This mock reqires an arguemnt of 8")
      return 0b10110001

    def test_randomize(self):
      a = BitwiseData(8, 0b00011011)
      b = a.randomize(rng=self.mock_rng8)
      self.assertEqual(a, BitwiseData(8, 0b10110001))
      self.assertEqual(b, a)

    def test_reversed(self):
      a = BitwiseData(8, 0b01110001)
      b = a.reversed()
      self.assertEqual(b, BitwiseData(8, 0b10001110))

  if __name__ == '__main__':
    unittest.main()
