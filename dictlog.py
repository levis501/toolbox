#!/usr/bin/env python


class DictLog:
  def __setattr__(self, key, value):
    if key in self.__dict__:
      self.__dict__[key].append(value)
    else:
      self.__dict__[key] = [value]
  def __getattr__(self, key):
    if key in self.__dict__:
      return self.__dict__[key] 
    else:
      self.__dict__[key] = []
      return self.__dict__[key]
