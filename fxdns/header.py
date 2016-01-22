from fxdns.prototypes import *
import struct


field_order = ['query','answer','authority','additional']

def _bx(n,pad=8):
  s = bin(n)[2:]
  return s.rjust(pad,'0')[:pad][::-1]

def get_bit(m,b):
  pass

class BitMapping(object):
  config = None
  names = None
  bitlen = 8
  mask_mask = 0

  def __init__(self, bitlen=8, **kw):
    print kw
    self.config = dict()
    self.names = []
    self.bitlen = bitlen
    self.mask_mask = int('1'*self.bitlen,2)
    for name, args in kw.iteritems():
      offset, size = args
      mask =  self.mask_mask & ((1 << size)-1)<<offset
      self.config[name] = dict(offset=offset, size=size, mask=mask)
      self.names.append(name)

  def iter_get_values(self, source):
    for name in self.names:
      entry = self.config[name]
      val = (self.mask_mask & source & entry['mask']) >> entry['offset']
      yield name, val



class FxDnsFlags(WireInterface):

  qr = 0
  opcode = 0
  aa = 0
  tc = 0
  rd = 0
  ra = 0
  z = 0
  rcode = 0

  _bin_map = BitMapping(
      qr=(0, 1),
      opcode=(1, 4),
      aa=(5, 1),
      tc=(6, 1),
      rd=(7, 1),
      ra=(8, 1),
      z=(9, 3),
      rcode=(12, 4)
  )

  def unpack(self, source):
    w = struct.unpack("!H", source)[0]
    print "Flag Word:", w, _bx(w,16)
    for  name, value  in self._bin_map.iter_get_values(w):
      setattr(self, name, value)

  def __str__(self):
    return "".join(('{0}:{1} ; '.format(key,getattr(self,key))) for key in self._bin_map.names)


class FxDnsHeader(WireInterfaceEx):
  _min_size = 12
  idx = 0
  flags = None
  count = None

  def on_init(self):
    self.idx = 0
    self.flags = FxDnsFlags()
    self.count = {}
    for key in field_order:
      self.count[key] = 0

  def _unpack(self, source):
    print source
    source = make_exstrio(source)
    self.idx = source.read_single_fmt("!H")
    self.flags = FxDnsFlags(source.read_single_fmt("2s"))
    for key in field_order:
      self.count[key] = source.read_single_fmt("!H")

  def __str__(self):
    ret = ""
    ret += " | ID: {0}\n".format(self.idx)
    ret += " | FLAGS: {0}\n".format(self.flags)
    ret += " | COUNT: {0}".format(self.count.values())
    return ret

def unpack(source):
  return FxDnsHeader(source)