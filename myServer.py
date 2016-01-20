import SocketServer
import threading
import signal
import socket
import struct

def socket_orginal_dst(s):
  SO_ORIGINAL_DST = 80
  try :
    dst = s.getsockopt(socket.SOL_IP, SO_ORIGINAL_DST, 16)
    srv_port, srv_ip = struct.unpack("!2xH4s8x", dst)
    srv_addr = str(socket.inet_ntoa(srv_ip))
    return (srv_addr,srv_port)
  except :
    return None

class SrvPrototype(object):
  server_type = None
  server_id = None
  callback = None

class MyTcpServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer, SrvPrototype):
  server_type = "TCP"
  allow_reuse_address = True
  daemon_threads = True


class MyUdpServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer, SrvPrototype):
  server_type = "UDP"
  allow_reuse_address = True
  daemon_threads = True


_TCP_STR = 'tcp'
_UDP_STR = 'udp'
PROTO_TCP = [ _TCP_STR ]
PROTO_UDP = [ _UDP_STR ]

def tcp_query_response(connection, address, server):
  print "++ TCP"
  pass

def udp_query_response(connection, address, server):
  print "++ UDP"
  pass


class IpServices(object):
  servers = None
  threads = None
  tcp_proxy = tcp_query_response
  udp_proxy = udp_query_response

  def __init__(self, handler=None):
    self.servers = []
    self.threads = []
    self.handler = handler

  def _server_start_thread(self, server_no, server):
    print "Starting server", server
    server.serve_forever()
    print "Done serving ..."

  def _add_srv(self, srv_class, listen_on, proxy):
    srv = srv_class(listen_on, proxy)
    print "New instance ", srv, listen_on
    srv.callback = self.handler
    srv_no = len(self.servers)
    srv.server_id = srv_no
    th = threading.Thread(target=self._server_start_thread, args=[srv_no, srv])
    th.daemon = True
    self.servers.append(srv)
    self.threads.append(th)

  def add(self, port, proto=None, address=None):
    do_tcp = True
    do_udp = True
    if address is None:
      address = '0.0.0.0'
    listen_address = (address, int(port))
    if proto is not None:
      if _TCP_STR not in proto:
        do_tcp = False
      if _UDP_STR not in proto:
        do_udp = False
    if do_tcp:
      self._add_srv(MyTcpServer, listen_address, self.tcp_proxy)
    if do_udp:
      self._add_srv(MyUdpServer, listen_address, self.udp_proxy)

  def start(self):
    for th in self.threads:
      th.start()

  def stop(self):
    for srv in self.servers:
      srv.shutdown()
      srv.server_close()

  def wait_for_all(self):
    for th in self.threads:
      if th.isAlive():
        th.join()









#x = TCPUDPmachine("0.0.0.0",3333,messageHandlerClass)
#x.run()


