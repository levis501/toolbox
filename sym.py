# for use as %run in ipython 

from sympy import *

def es(q,n=2):
  if n <= 0:
    return q
  return es(simplify(expand(q)),n-1)


def cmp(a,b,n=2):
  return sign(es(es(a,n)-es(b,n),n))

def eq(a,b,n=2):
  return cmp(a,b)==0

sym=symbols
