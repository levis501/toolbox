#!/usr/bin/env python3

# binary.py


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

def bitStr(a, n):
	return ''.join([repr(num) for num in getBits(a,n)])[::-1]

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

MASK_256 = (1 << 256) - 1
def invert(a, bitCount=None):
	global MASK_256
	b = 0
	while (a > 0):
		c = MASK_256 - (a & MASK_256)
		b = (b << 256) | c
		a >>= 256
	if bitCount == None:
		return b
	return b & ((1 << bitCount)-1)
