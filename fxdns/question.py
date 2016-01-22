from fxdns.prototypes import  *

import fxdns.name


class FxDnsQuestion(WireInterfaceEx):
  qname = None
  qtype = None
  qclass = None

  def _unpack(self, source):
    self.qname = fxdns.name.read_name(source)
    self.qtype, self.qclass = source.read_fmt("!HH")


  def __str__(self):
    qn = ""
    for label in self.qname:
      qn += "({0}){1} ".format(len(label), label)
    return "QUERY: [{0}] [{1}] [{2}] ?".format(qn, self.qtype, self.qclass)


def unpack(source):
  return FxDnsQuestion(source)