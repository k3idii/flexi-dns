from fxdns.prototypes import  *

import fxdns.header
import fxdns.question
import fxdns.resource


class FxDnsPacket(WireInterfaceEx):
  _dump = True
  header = None
  query = None
  answer = None
  authority = None
  additional = None
  _readers = {
    'query' : fxdns.question.unpack,
    'answer' : fxdns.resource.unpack,
    'authority' : fxdns.resource.unpack,
    'additional' : fxdns.resource.unpack
  }

  def on_init(self):
    for f in fxdns.header.field_order:
      setattr(self, f, [])

  def _unpack(self, source):
    self.header = fxdns.header.unpack(source)
    print self.header
    for f in fxdns.header.field_order:
      for i in range(self.header.count[f]):
        print "Reading {0} {1} of {2}".format(f, i+1, self.header.count[f])
        reader = self._readers.get(f, None)
        if callable(reader):
          entry = reader(source)
          print " -> ", str(entry)
          getattr(self,f).append(entry)

  def is_valid_query(self):
    return True


def unpack(source):
  return FxDnsPacket(source)

def to_answer(query):
  return None




