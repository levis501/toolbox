#!/usr/bin/env python3

# print statstics of the floating point data presented at stdin

import sys

from math import sqrt

class Stats:
  MAX_UNIQUES_UNFLAGGED=16384
  def __init__(self, initialData=[], trackUniques=False):
    self.dataCount = 0
    self.dataSum = 0
    self.dataSquaredSum = 0
    self.dataMax = None
    self.dataMin = None
    self.trackUniques = trackUniques
    self.dataUniques = set()
    self.addAll(initialData)
#    if trackUniques:
#      self.dataUniques = set()
#    else:
#      self.dataUniques = None

  def add(self, datum):
    self.dataCount += 1
    self.dataSum += datum
    self.dataSquaredSum += datum*datum
    try:
      if self.dataMax < datum:
        self.dataMax = datum
      if self.dataMin > datum:
        self.dataMin = datum
    except:
      self.dataMax = datum
      self.dataMin = datum
    if self.dataUniques != None:
      self.dataUniques.add(datum)
      if (not self.trackUniques) and (len(self.dataUniques) > Stats.MAX_UNIQUES_UNFLAGGED):
        self.dataUniques = None

  def addAll(self, data):
    for datum in data:
      self.add(datum)

  def avg(self):
    if self.dataCount==0:
      return "undef"
    return self.dataSum / self.dataCount

  def avg2(self):
    if self.dataCount==0:
      return "undef"
    return self.dataSquaredSum / self.dataCount

  def sum(self):
    return self.dataSum

  def max(self):
    return self.dataMax

  def min(self):
    return self.dataMin

  def N(self):
    return self.dataCount

  def uniqueCount(self):
    if self.dataUniques == None:
      return "enable with -u or --unique, or Stats(trackUniques=True) (requires more memory)"
    else:
      return len(self.dataUniques)

  def std(self):
    if self.dataCount==0:
      return "undef"
    return sqrt(self.avg2() - self.avg()**2)

  def print(self):
    print("       number of items: " + str(self.N()))
    print("number of unique items: " + str(self.uniqueCount()))
    print("                   sum: " + str(self.sum()))
    print("                  mean: " + str(self.avg()))
    print("                   max: " + str(self.max()))
    print("                   min: " + str(self.min()))
    print("    standard deviation: " + str(self.std()))

if __name__=='__main__':
    # load data
    stats = Stats(trackUniques="--unique" in sys.argv or "-u" in sys.argv)
    for line in sys.stdin.readlines():
      for item in line.split():
        try:
          i = float(item)
          stats.add(i)
        except ValueError:
          continue
    stats.print()


class Freq:
  def __init__(self, initialItems = ()):
    self.items = {}
    for item in initialItems:
      self.add(item)
  def add(self, item):
    try:
      self.items[item] += 1
    except KeyError:
      self.items[item] = 1
  def byFrequency(self):
    return sorted(self.items.items(), key=lambda i:i[1])
  def byValues(self):
    return sorted(self.items.items(), key=lambda i:i[0])
