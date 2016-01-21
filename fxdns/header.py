from fxdns.prototypes import *

class FxDnsHeader(WireInterface):
  pass



def unpack(source):
  return FxDnsHeader(source)