from misc.exstrio import make_exstrio


def _abstract_(f):  # We srsly do not need abc.abstradmethod here
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
  _min_size = 0
  _dump = False

  # @exstrio_wrapper('source')
  def unpack(self, source):
    source = make_exstrio(source)
    if self._dump:
      print source.hex_dump(title=self.__class__)
    if self._min_size > 0:
      available = source.available_bytes()
      if available < self._min_size:
        raise Exception("Expected {0} bytes, have {1}".format(self._min_size, available))
    self._unpack(source)

  @_abstract_
  def _unpack(self, source):
    pass
