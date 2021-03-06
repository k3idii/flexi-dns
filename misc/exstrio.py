from StringIO import StringIO
import struct
import os


def glue_ex(parts, delim='', preproc=None):
  if preproc:
    if isinstance(preproc, list):
      for fn in preproc:
        parts = map(fn, parts)
    elif callable(preproc):
      parts = map(preproc, parts)
  return delim.join(parts)


def unpack_ex(fmt, data, into=None):
  size = struct.calcsize(fmt)
  if len(data) < size:
    raise Exception("unpack_ex: too few bytes to unpack !")
  parts = struct.unpack(fmt, data)
  if not parts:
    return None
  if not into:
    return parts
  if len(parts) > len(into):
    raise Exception("unpack_ex: too many values unpacked !")
  return dict((into[i], parts[i]) for i in range(len(parts)))


def make_exstrio(arg):
  if isinstance(arg, ExStrIO):
    return arg
  return ExStrIO(arg)


def exstrio_wrapper(pos_or_name=1, arg_is_pos=None):
  if not arg_is_pos:
    if isinstance(pos_or_name, int):
      arg_is_pos = True
    else:
      arg_is_pos = False

  def _wrap1(f):

    def _wrap2_name(*a, **kw):
      if pos_or_name in kw:
        kw[pos_or_name] = make_exstrio(kw[pos_or_name])
      else:
        a = list(a)
        idx = f.func_code.co_varnames.index(pos_or_name)
        a[idx] = make_exstrio(a[idx])
      return f(*a, **kw)

    def _wrap2_pos(*a, **kw):
      a = list(a)
      a[pos_or_name] = make_exstrio(a[pos_or_name])
      return f(*a, **kw)

    if arg_is_pos:
      return _wrap2_pos
    else:
      return _wrap2_name

  return _wrap1


class ExStrIO(StringIO):
  _jump_stack = None

  def __init__(self, *a, **kw):
    self._jump_stack = list()
    StringIO.__init__(self, *a, **kw)

  def read_n(self, n):
    d = self.read(n)
    if not d or len(d) < n:
      raise Exception("Read error : need %d bytes, got %d " % (n, len(d)))
    return d

  def read_fmt(self, fmt="", into=None):
    sz = struct.calcsize(fmt)
    d = self.read_n(sz)
    return unpack_ex(fmt, d, into)

  def read_single_fmt(self, fmt):
    v = self.read_fmt(fmt)
    if v:
      return v[0]
    else:
      return None

  def read_the_rest(self):
    n = self.available_bytes()
    return self.read_n(n)

  def append(self, data):
    p = self.tell()
    self.seek(0, os.SEEK_END)
    self.write(data)
    self.seek(p)

  def append_fmt(self, fmt, *a):
    return self.append(struct.pack(fmt, *a))

  def write_fmt(self, fmt, *a):
    return self.write(struct.pack(fmt, *a))

  def printf(self, fmt, *a, **kw):
    self.write(fmt.format(*a, **kw))

  def read_all(self):
    p = self.tell()
    self.seek(0)
    v = self.read()
    self.seek(p)
    return v

  def dump(self):
    return self.getvalue()

  def dumpf(self, filename):
    open(filename, 'w').write(self.getvalue())

  def loadf(self, filename):
    self.__init__(open(filename, 'r').read())

  def available_bytes(self):
    org = self.tell()
    self.seek(0, os.SEEK_END)
    end = self.tell()
    self.seek(org)
    return end - org

  def get_pos(self):
    return self.tell()

  def push(self):
    self._jump_stack.append(self.tell())

  def pop(self, restore_position=False):
    if restore_position:
      self.seek(self._jump_stack.pop(), os.SEEK_SET)
    else:
      self._jump_stack.pop()

  def goto(self, pos):
    self.seek(pos, os.SEEK_SET)

  def hex_dump(self, columns=16, title=None, head=True):
    rets = ' \n'
    if head:
      if title:
        rets += " .----[ %s ]----- \n" % title
      rets += "| offset          ascii                 hex   \n"
    p = self.tell()  # save
    self.seek(0)  # rewind
    fmt = "| 0x%08X %-" + str(columns) + "s \t %s\n"
    while True:
      of = self.tell()
      chunk = self.read(columns)
      hx = ''
      ch = ''
      for c in list(chunk):
        ch += c if 32 <= ord(c) < 127 else '.'
        hx += "%02X " % ord(c)
      rets += fmt % (of, ch, hx)
      if len(chunk) < columns:
        break
    rets += "| 0x%08X \n" % self.tell()
    rets += "`-- \n"
    self.seek(p)
    return rets
