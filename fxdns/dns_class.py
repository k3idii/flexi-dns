import sys

forward = {'IN': 1, 'CS': 2, 'CH': 3, 'HS': 4, 'ANY': 255}

rev = {}

_m = sys.modules[__name__]
for k, v in forward.iteritems():
 setattr(_m, k, v)
 rev[v] = k