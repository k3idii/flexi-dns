import argparse
import struct
import logging

logging.basicConfig(level=logging.DEBUG)

import myServer

org_read = myServer.tcp_receive_all


def new_read(sock):
  fmt = "!H"
  size = struct.calcsize(fmt)
  sock.settimeout(1)
  prefix = sock.recv(size)
  assert len(prefix) == size, "Expected {0} bytes at TCP prefix".format(size)
  expected_size = struct.unpack(fmt, prefix)[0]
  data = org_read(sock, max_size=expected_size)
  assert len(data) == expected_size, "Expected {0} bytes at TCP data".format(expected_size)
  return data


myServer.tcp_receive_all = new_read  # Fix difference in dns tcp & udp


def get_func_by_path(p):
  mod_name, func_name = p.rsplit(".", 1)
  mod_handle = __import__(mod_name)
  return getattr(mod_handle, func_name)


def main():
  a = argparse.ArgumentParser(description="Flexi DNS Server")
  a.add_argument('--listen', type=str, default=[], help="Listen address, Format: ip:port/proto", action='append')
  a.add_argument('--handler', type=str, help="handler path (package.function)", required=True)
  args = a.parse_args()

  s = myServer.IpServices(get_func_by_path(args.handler))
  for spec in myServer.parse_listen_args(args.listen, as_dict=True):
    s.add(**spec)
  s.idle_loop()


if __name__ == "__main__":
  main()
else:
  print "This is MAIL module, you should run it !"
