import sys

forward = {'A': 1, 'NS': 2, 'CNAME': 5, 'SOA': 6, 'PTR': 12, 'MX': 15, 'TXT': 16, 'AAAA': 28, 'SRV': 33, 'SPF': 99,
           'ANY': 255}

rev = {}

_m = sys.modules[__name__]
for k, v in forward.iteritems():
 setattr(_m, k, v)
 rev[v] = k

