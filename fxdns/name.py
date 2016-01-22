import misc.exstrio
import struct


@misc.exstrio.exstrio_wrapper(0)
def read_name(source):

  jumped = False

  @misc.exstrio.exstrio_wrapper(0)
  def read_single_label(source):
    b = source.read_n(1)
    val = ord(b)
    if val == 0:
      return None, 0
    if val & 0xC0:
      tgt = struct.unpack("!H",b+source.read_n(1))[0] & 0x3fff
      if not read_name.jumped:
        source.push() # store position
        read_name.jumped = True
      source.goto(tgt)
      return None, -1
    else:
      return source.read_n(val), val

  result = []
  while True:
    n,l = read_single_label(source)
    if l == 0:
      break
    if l > 0:
      result.append(n)
  if jumped:
    source.pop()
  return result