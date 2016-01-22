import SocketServer
import threading
import socket
import struct
import select
import logging

SRV_TCP_STR = 'tcp'
SRV_UDP_STR = 'udp'
PROTO_TCP = [SRV_TCP_STR]
PROTO_UDP = [SRV_UDP_STR]

_PROTO_ANY = 'any'
_HOST_ANY = '0.0.0.0'
PROTO_ALL = PROTO_TCP + PROTO_UDP


def parse_listen_args(list_of_spec, as_dict=False):
  for entry in list_of_spec:
    if ":" not in entry:
      raise Exception("Invalid listen-address syntax: {0}".format(entry))
    if "/" in entry:
      entry, proto = entry.split("/", 1)
      if proto == _PROTO_ANY:
        proto = PROTO_ALL
      else:
        proto = [proto]
    else:
      proto = PROTO_ALL
    print entry.split(":")
    host, port = entry.split(":")
    port = int(port)
    if len(host) < 1:
      host = _HOST_ANY
    if as_dict:
      yield dict(host=host, port=port, proto=proto)
    else:
      yield host, port, proto


def socket_orginal_dst(s):
  SO_ORIGINAL_DST = 80
  try:
    dst = s.getsockopt(socket.SOL_IP, SO_ORIGINAL_DST, 16)
    srv_port, srv_ip = struct.unpack("!2xH4s8x", dst)
    srv_addr = str(socket.inet_ntoa(srv_ip))
    return (srv_addr, srv_port)
  except:
    return None


class SrvPrototype(object):
  server_type = None
  server_id = None
  callback = None


class MyTcpServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer, SrvPrototype):
  server_type = SRV_TCP_STR
  allow_reuse_address = True
  daemon_threads = True


class MyUdpServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer, SrvPrototype):
  server_type = SRV_UDP_STR
  allow_reuse_address = True
  daemon_threads = True


def tcp_receive_all(sock, timeout=2, chunk_size=2048, max_size=None):
  q = select.poll()
  q.register(sock.fileno(), select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
  data = ''
  while True:
    ev = q.poll(timeout)
    if len(ev) != 1:
      return data
    fd, flag = ev[0]
    if not (flag & (select.POLLIN | select.POLLPRI)):
      return data
    if max_size:
      recv_size = min(chunk_size, max_size)
    else:
      recv_size = chunk_size
    chunk = sock.recv(recv_size)
    if not len(chunk) > 0:
      return data
    data += chunk
    if max_size:
      max_size -= len(chunk)
      if max_size <= 0:  # detect underflow !?
        return data


def tcp_query_response(connection, address, server):
  message = tcp_receive_all(connection)
  response = server.callback(server, address, message)
  if response:
    connection.sendall(response)


def udp_query_response(data, address, server):
  message, sock = data
  response = server.callback(server, address, message)
  if response:
    sock.sendto(response, address)


def dummy_handler(server, address, message):
  pass


class IpServices(object):
  servers = None
  threads = None
  services = None

  def __init__(self, handler=None):
    self.services = []
    self.servers = []
    self.threads = []
    self.handler = handler if handler else dummy_handler

  def _server_start_thread(self, server):
    logging.info("Starting server {0} ... ".format(repr(server)))
    try:
      server.serve_forever()
    except Exception as err:
      logging.error("Fail on listen loop: {0}".format(str(err)))
    logging.info("Stopping server {0} ... ".format(repr(server)))

  def _add_srv(self, srv_class, listen_on, proxy):
    self.services.append((srv_class, listen_on, proxy))
    logging.info("Will listen on {0}  ".format(listen_on))

  def add(self, port, host=None, proto=None):
    do_tcp = True
    do_udp = True
    if host is None:
      host = '0.0.0.0'
    listen_address = (host, int(port))
    if proto is not None:
      if SRV_TCP_STR not in proto:
        do_tcp = False
      if SRV_UDP_STR not in proto:
        do_udp = False
    if do_tcp:
      self._add_srv(MyTcpServer, listen_address, tcp_query_response)
    if do_udp:
      self._add_srv(MyUdpServer, listen_address, udp_query_response)

  def start(self):
    for entry in self.services:
      srv_class, listen_on, proxy = entry
      logging.info("Start listener {0} on {1} ".format(repr(srv_class), listen_on))
      srv = srv_class(listen_on, proxy)
      srv.callback = self.handler
      srv_no = len(self.servers)
      srv.server_id = srv_no
      self.servers.append(srv)
      th = threading.Thread(target=self._server_start_thread, args=[srv])
      th.daemon = True
      self.threads.append(th)
      th.start()

  def stop(self):
    for srv in self.servers:
      srv.shutdown()
      srv.server_close()

  def wait_for_all(self):
    for th in self.threads:
      if th.isAlive():
        th.join()

  def idle_loop(self, sleep_time=0.1):

    import signal
    import time

    def sig_stop(s, _):
      logging.info("STOP SIGNAL {0}".format(s))
      self.stop()

    def sig_hup(s, _):
      logging.info("HUP SIGNAL {0}".format(s))
      self.stop()
      self.wait_for_all()
      self.start()

    signal.signal(signal.SIGTERM, sig_stop)
    signal.signal(signal.SIGTERM, sig_stop)
    signal.signal(signal.SIGHUP, sig_hup)

    self.start()
    try:
      while True:
        time.sleep(sleep_time)
    except KeyboardInterrupt:
      logging.info("STOP: KeyboardInterrupt")
      self.stop()
    self.wait_for_all()
