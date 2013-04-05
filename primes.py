#!/usr/bin/env python3.2

from math import sqrt, ceil

# factor product of two primes


def factor_2p_recursive(product, a=None, b=None):
    if a==None:
        s = sqrt(product)
        return factor_2p_recursive(product, int(s), ceil(s))
    delta = product - a*b
    if int(delta)==0:
        return (int(a), int(b))
    if delta > 0:
        b = ceil(b + delta/a)
    else:
        a = int(a + delta/b)
    return factor_2p_recursive(product, a, b)


def ceil_int_divide(num, den):
    idiv = num//den
    if (idiv * den) == num:
        return idiv
    else:
        return idiv+1

def factor_2p(product, a=None, b=None):
    if a==None:
        s = sqrt(product)
        a = int(s)
        b = ceil(s)
    delta = product - a*b
    while int(delta) != 0:
        print("%d %d %d" % (a,b,delta))
        if delta > 0:
            b = b + ceil_int_divide(delta,a)
        else:
            a = a + delta//b
        delta = product - a*b
    return (int(a), int(b))
    


def primes_under(N):
    S = set(range(2,N+1))
    i = 2
    while i <= N:
        if not i in S:
            i += 1
        else:
            j = i*2
            while j <= N:
                if j in S:
                    S.remove(j)
                j += i
            i += 1
    L = list(S)
    L.sort()
    return L

