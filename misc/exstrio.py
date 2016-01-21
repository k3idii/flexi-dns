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


def make_exstrio(pos_or_name=1, arg_is_pos = None):

  if not arg_is_pos:
    if isinstance(pos_or_name, int):
      arg_is_pos = True
    else:
      arg_is_pos = False

  def _fix(arg):
    if isinstance(arg, ExStrIO):
      return arg
    return ExStrIO(arg)

  def _wrap1(f):

    def _wrap2_name(*a, **kw):
      if pos_or_name in kw:
        kw[pos_or_name] = _fix(kw[pos_or_name])
      else:
        a = list(a)
        idx = f.func_code.co_varnames.index(pos_or_name)
        a[idx] = _fix(a[idx])
      return f(*a, **kw)

    def _wrap2_pos(*a , **kw):
      a = lista(a)
      a[pos_or_name] = _fix(a[pos_or_name])
      return f(*a, **kw)

    if arg_is_pos :
      return _wrap2_pos
    else:
      return _wrap2_name

  return _wrap1


class ExStrIO(StringIO):
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
    n =  self.available_bytes()
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

  def hex_dump(self, bytes=16, title=None, head=True):
    S = ' \n'
    if head:
      if title:
        S += " .----[ %s ]----- \n" % title
      S += "| offset          ascii                 hex   \n"
    p = self.tell()  # save
    self.seek(0)  # rewind
    fmt = "| 0x%08X %-" + str(bytes) + "s \t %s\n"
    while True:
      of = self.tell()
      chunk = self.read(bytes)
      hx = ''
      ch = ''
      for c in list(chunk):
        ch += c if ord(c) >= 32 and ord(c) < 127 else '.'
        hx += "%02X " % ord(c)
      S += fmt % (of, ch, hx)
      if len(chunk) < bytes:
        break
    S += "| 0x%08X \n" % self.tell()
    S += "`-- \n"
    self.seek(p)
    return S

