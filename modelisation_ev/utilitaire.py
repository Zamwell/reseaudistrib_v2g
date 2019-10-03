# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 16:41:04 2019

@author: Utilisateur
"""


def trouv_break(li,start,combo):
    lo = li[start:]
    for i in range(len(lo)-1):
        if lo[i] == combo and lo[i+1] != combo:
            return i+start
    return None
    
def flatten(li):
    for x in li:
        if hasattr(x, '__iter__') and not isinstance(x, str):
            for y in flatten(x):
                yield y
        else:
            yield x
            
def encadrer(valmin, val, valmax):
    if val < valmin:
        return valmin
    elif val > valmax:
        return valmax
    else:
        return val