from misc.exstrio import make_exstrio

def _abstract_(f): # We srsly do not need abc.abstradmethod here
  def _msg(*a, **kw):
    raise Exception("IMPLEMENT ME: {0}".format(str(f)))
  return _msg


class WireInterface(object):

  def __init__(self, source=None):
    self.on_init()
    if source is not None:
      self.unpack(source)

  def on_init(self):
    pass

  @_abstract_
  def pack(self):
    return None

  @_abstract_
  def unpack(self, source):
    pass


class WireInterfaceEx(WireInterface):

  @make_exstrio('source')
  def unpack(self, source):
    self._unpack(source)

  @_abstract_
  def _unpack(self, source):
    pass

