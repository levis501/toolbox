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

  @staticmethod
  def randomized(count, rng=random.getrandbits):
    return BitwiseData(count, rng(count))
  def withRandomizedValue(self, rng=random.getrandbits):
    return BitwiseData.randomized(self.count, rng)
  def __len__(self):
    return self.count
  def withSetBits(self, bits, start=0, count=None):
    if count is None:
      count = self.count-start
    value = setBits(self.value, bits, start, count)
    return self.withValue(value)
  def withValue(self, value):
    return BitwiseData(self.count, value)
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
    if key < 0:
      key = self.count + key
    return getBit(self.value, key)
  def withSetBit(self, n, b):
    return BitwiseData(self.count, setBit(self.value, n, b))
  def withDeletedBit(self, n):
    highBits = ((self.value >> (n+1)) << n) 
    if (n > 0):
      lowBits = self.value & invert(0, n-1)
    else:
      lowBits = 0
    return BitwiseData(self.count-1, highBits | lowBits)
  def withFlippedBit(self, b):
    return self.withValue(self.value ^ (1 << b))
  def withFlips(self, bitsToFlip):
    value = self.value
    for b in bitsToFlip:
      value ^= (1 << b)
    return self.withValue(value)

  def bitStr(self, separationWidth = None, separationCharacter=' '):
    if separationWidth == None:
      separationWidth = BitwiseData.DEFAULT_STRING_SEPARATION
    return bitStr(self.value, self.count, separationWidth, separationCharacter)
  def __or__(self, other):
    if type(other) == BitwiseData:
      value = self.value | other.value
      count = max(self.count, other.count)
    else:
      value = self.value | other
      count = max(self.count, highestOneIndex(other))
    return BitwiseData(count, value)
  def __xor__(self, other):
    if type(other) == BitwiseData:
      value = self.value ^ other.value
      count = max(self.count, other.count)
    else:
      value = self.value ^ other
      count = max(self.count, highestOneIndex(other))
    return BitwiseData(count, value)
  def __and__(self, other):
    if type(other) == BitwiseData:
      value = self.value & other.value
      count = max(self.count, other.count)
    else:
      value = self.value & other
      count = max(self.count, highestOneIndex(other))
    return BitwiseData(count, value)
  def __invert__(self):
    value = invert(self.value, self.count)
    return BitwiseData(self.count, value)
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
  def __mul__(self, other):
    if type(other)==int:
      """Repeat a BD n times"""
      n = other
      v = 0 
      for _ in range(n):
        v <<= self.count
        v += self.value
      return BitwiseData(self.count * n, v)
    raise TypeError(f"Unsupported operand type {type(other)}")
  def append(self, other):
    if type(other) != BitwiseData:
      other = BitwiseData.convert(other)
    c = self.count + other.count
    v = (other.value << self.count) + self.value
    return BitwiseData(c, v)
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
  def withCapacityIncreasedBy(self, increaseAmount):
    bd = BitwiseData(self.count + increaseAmount, self.value)
    return bd.withZeros(bd.count - increaseAmount, increaseAmount)
  def bitDistance(self, other):
    return bitDistance(self.value, other.value if type(other)==BitwiseData else other)
  def withAllZeros(self):
    return self.withValue(0)
  def withAllOnes(self):
    return self.withValue(invert(0, self.count))
  def withZeros(self, start, count):
    return self.withSetBits(0, start, count)
  def withOnes(self, start, count):
    return self.withSetBits(invert(0, count), start, count)
  def split(self, n):
    return list([self[k:k+n] for k in range(0, self.count, n)])
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
  def withRshift(self, n):
    return self.withValue(rshift(self.value, self.count, n))
  def __rshift__(self, n):
    return self.withRshift(n)
  def withLshift(self, n):
    return self.withValue(lshift(self.value, self.count, n))
  def __lshift__(self, n):
    return self.withLshift(n)
  def correlate(self, other):
    return self.count - 2 * self.bitDistance(other)
  def reversed(self):
    return BitwiseData.convert(reversed(self))
  def appendedWith(self, appendage):
    appendage = BitwiseData.convert(appendage)
    original_count = self.count
    larger = self.withCapacityIncreasedBy(appendage.count)
    return larger.withSetBits(appendage.value, original_count)

  @staticmethod
  def concat(a, b=None):
    if (b == None):
      c = functools.reduce(BitwiseData.concat, a)
    else:
      c = a.appendedWith(b)
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

  @staticmethod
  def convertBytes(origin, msb_first = False):
    if type(origin) != bytes:
      raise NotImplementedError(f'convertBytes only works on type "bytes", not "{type(origin)}"')
    bd_array = [BitwiseData(8, b, msb_first) for b in origin]
    return BitwiseData.concat(bd_array)

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
      a = BitwiseData(4)
      self.assertEqual(a[2], 0)
      b = a.withSetBit(2, 1)
      self.assertEqual(b[2], 1)
      c = a.withSetBit(2, 0)
      self.assertEqual(c[2], 0)

    def test_setBits(self):
      a = BitwiseData(8, 0b11010111)
      b = a.withSetBits(0b1010, 2, 4)
      self.assertEqual(b, 0b11101011)

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
      
    def test_mul(self):
      bd3 = BitwiseData(3, 0b110)
      bd6 = bd3 * 2
      self.assertEqual(bd6, BitwiseData(6, 0b110110))
      self.assertEqual(bd6 * 2, bd3 * 4)
      
    def test_append(self):
      a = BitwiseData(3, 0b101)
      b = BitwiseData(3, 0b011)
      self.assertEqual(a.append(b), BitwiseData(6, 0b011101))

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
      b = a.withCapacityIncreasedBy(1)
      self.assertEqual(len(b), 9)
      c = b.withCapacityIncreasedBy(10)
      self.assertEqual(len(c), 19)

    def test_bitDistance(self):
      a = BitwiseData(8, 0b10100101)
      b = BitwiseData(8, 0b00001111)
      self.assertEqual(a.bitDistance(b), 4)
      c = BitwiseData(4, 0b1111)
      self.assertEqual(b.bitDistance(c), 0)

    def test_setAll(self):
      a = BitwiseData(8, 0b10100101)
      self.assertEqual(a.countOnes(), 4)
      b = a.withAllZeros()
      self.assertEqual(b.countOnes(), 0)
      c = BitwiseData(8, 0b00001111)
      self.assertEqual(c.countOnes(), 4)
      d = c.withAllOnes()
      self.assertEqual(d.countOnes(), 8)

    def test_getIndexedBits(self):
      a = BitwiseData(8, 0b10100111)
      l = [1, 1, 1, 0, 0, 1, 0, 1]
      for (i, b) in a.getIndexedBits():
        self.assertEqual(b, l[i])

    def test_setZeros(self):
      a = BitwiseData(8, 0b10100111)
      b = BitwiseData(8, 0b10000011)
      c = a.withZeros(2, 5)
      self.assertEqual(c, b)

    def test_setOnes(self):
      a = BitwiseData(8, 0b10100111)
      b = BitwiseData(8, 0b11111111)
      c = a.withOnes(2, 5)
      self.assertEqual(c, b)

    def test_substr(self):
      a = BitwiseData(8, 0b10100111)
      self.assertEqual(a.substr(0, 3), BitwiseData(3, 0b111))
      self.assertEqual(a.substr(1, 4), BitwiseData(4, 0b0011))
      self.assertEqual(a.substr(2, 5), BitwiseData(5, 0b01001))
      self.assertEqual(a.substr(3, 5), BitwiseData(5, 0b10100))

    def test_delitem(self):
      a = BitwiseData(8, 0b10100111)
      b = a.withDeletedBit(4)
      self.assertEqual(b, BitwiseData(7, 0b1010111))
      c = b.withDeletedBit(4)
      self.assertEqual(c, BitwiseData(6, 0b100111))
      d = c.withDeletedBit(0)
      self.assertEqual(d, BitwiseData(5, 0b10011))
      e = d.withDeletedBit(4)
      self.assertEqual(e, BitwiseData(4, 0b0011))
      
    def test_rshift(self):
      a = BitwiseData(5, 0b11010)
      b = a.withRshift(1)
      self.assertEqual(b, BitwiseData(5, 0b01101))
      c = b.withRshift(2)
      self.assertEqual(c, BitwiseData(5, 0b01011))
      d = c.withRshift(3)
      self.assertEqual(d, BitwiseData(5, 0b01101))
      e = d.withRshift(4)
      self.assertEqual(e, BitwiseData(5, 0b11010))
      f = e.withRshift(5)
      self.assertEqual(f, BitwiseData(5, 0b11010))
      g = f.withRshift(6)
      self.assertEqual(g, BitwiseData(5, 0b01101))
      
    def test_lshift(self):
      a = BitwiseData(5, 0b11010)
      b = a.withLshift(1)
      self.assertEqual(b, BitwiseData(5, 0b10101))
      c = b.withLshift(2)
      self.assertEqual(c, BitwiseData(5, 0b10110))
      d = c.withLshift(3)
      self.assertEqual(d, BitwiseData(5, 0b10101))
      e = d.withLshift(4)
      self.assertEqual(e, BitwiseData(5, 0b11010))
      f = e.withLshift(5)
      self.assertEqual(f, BitwiseData(5, 0b11010))
      g = f.withLshift(6)
      self.assertEqual(g, BitwiseData(5, 0b10101))

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
      c = a.appendedWith(b)
      self.assertEqual(c, BitwiseData(8, 0b01011010))
      d = c.appendedWith(1)
      self.assertEqual(d, BitwiseData(9, 0b101011010))
      e = d.appendedWith(0)
      self.assertEqual(e, BitwiseData(10, 0b0101011010))

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

    def testConvertBytes(self):
      a = bytes([0x0F, 0xAA])
      b = BitwiseData.convertBytes(a, msb_first=False)
      self.assertEqual(b, BitwiseData(16, 0xAA0F))
      c = BitwiseData.convertBytes(a, msb_first=True)
      self.assertEqual(c, BitwiseData(16, 0x55F0))

    def test_slice(self):
      a = BitwiseData(8, 0b10110100)
      self.assertEqual(a[:], 0b10110100)
      self.assertEqual(a[0:], 0b10110100)
      self.assertEqual(a[1:], 0b1011010)
      self.assertEqual(a[::-1], 0b00101101)
      self.assertEqual(a[5:3:-1], 0b11)

    def mock_rng(self, mockBitCount, mockBits):
      def rng(bitCount):
        self.assertEqual(bitCount, mockBitCount, f'This mock only responds to bit counts of {mockBitCount}')
        return mockBits
      return rng

    def test_randomize(self):
      a = BitwiseData(8, 0b00011011)
      mockBits8 = 0b10110001
      mock_rng8 = self.mock_rng(8, mockBits8)
      b = a.withRandomizedValue(rng=mock_rng8)
      self.assertEqual(b, BitwiseData(8, mockBits8))
      mockBits12 = 0b1001001110
      mock_rng12 = self.mock_rng(12, mockBits12)
      c = BitwiseData.randomized(12, rng=mock_rng12)
      self.assertEqual(c, BitwiseData(12, mockBits12))

    def test_reversed(self):
      a = BitwiseData(8, 0b01110001)
      b = a.reversed()
      self.assertEqual(b, BitwiseData(8, 0b10001110))

    def test_flips(self):
      a = BitwiseData(8, 0b01100101)
      b = a.withFlippedBit(2)
      self.assertEqual(b, BitwiseData(8, 0b01100001))
      c = a.withFlips([2,3,4])
      self.assertEqual(c, BitwiseData(8, 0b01111001))

    def test_split(self):
      a = BitwiseData(8, 0b01101001)
      a2 = a.split(2)
      self.assertEqual(a2[0], BitwiseData(2, 0b01))
      self.assertEqual(a2[1], BitwiseData(2, 0b10))
      self.assertEqual(a2[2], BitwiseData(2, 0b10))
      self.assertEqual(a2[3], BitwiseData(2, 0b01))
      a4 = a.split(4)
      self.assertEqual(a4[0], BitwiseData(4, 0b1001))
      self.assertEqual(a4[1], BitwiseData(4, 0b0110))
      
      
  if __name__ == '__main__':
    unittest.main()
