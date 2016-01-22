from fxdns.prototypes import  *
import fxdns.name


class FxDnsResource(WireInterfaceEx):
  qname = None
  qtype = None
  qclass = None
  ttl = 0
  rdata_len = 0
  rdata = None
  rdata_raw = None

  def _unpack(self, source):
    self.qname = fxdns.name.read_name(source)
    self.qtype, self.qclass = source.read_fmt("!HH")
    self.ttl, self.rdata_len = source.read_fmt("!IH")
    if self.rdata_len > 0:
      self.rdata_raw = source.read_n(self.rdata_len)
    else:
      self.rdata_raw = ''

  def __str__(self):
    qn = ""
    for label in self.qname:
      qn += "({0}){1} ".format(len(label), label)
    return """Resource: [{0}] [{1}] [{2}] [{3}] ({4})[{5}]""".format(qn, self.qtype, self.qclass, self.ttl, self.rdata_len, str(self.rdata_raw))





def unpack(source):
  return FxDnsResource(source)