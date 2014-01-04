#!/usr/bin/env python3

# print statstics of the floating point data presented at stdin

import sys

from math import sqrt

class Statistics:
  def __init__(self, trackUniques=False):
    self.dataCount = 0
    self.dataSum = 0
    self.dataSquaredSum = 0
    self.dataMax = None
    self.dataMin = None
    if trackUniques:
      self.dataUniques = set()
    else:
      self.dataUniques = None

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
      return "enable with -u or --unique (requires more memory)"
    else:
      return len(self.dataUniques)

  def std(self):
    if self.dataCount==0:
      return "undef"
    return sqrt(self.avg2() - self.avg()**2)


if __name__=='__main__':
    # load data
    stats = Statistics("--unique" in sys.argv or "-u" in sys.argv)
    for line in sys.stdin.readlines():
      for item in line.split():
        try:
          i = float(item)
          stats.add(i)
        except ValueError:
          continue


    print("       number of items: " + str(stats.N()))
    print("number of unique items: " + str(stats.uniqueCount()))
    print("                   sum: " + str(stats.sum()))
    print("                  mean: " + str(stats.avg()))
    print("                   max: " + str(stats.max()))
    print("                   min: " + str(stats.min()))
    print("    standard deviation: " + str(stats.std()))


