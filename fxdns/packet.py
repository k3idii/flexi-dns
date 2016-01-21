from fxdns.prototypes import  *

field_order = ['query','answer','authority','additional']

class FxDnsPacket(WireInterfaceEx):
  header = None
  query = None
  answer = None
  authority = None
  additional = None

  def on_init(self):
    for f in field_order
      setattr(self, f, [])

  def _unpack(self, source):
    print "OK"


def unpack(source):
  return FxDnsPacket(source)


