import myServer
import fxdns.packet


def handle(server, address, message):
  """
  :param myServer.SrvPrototype server:
  :param tuple address: tuple
  :param str message: str
  :return: None
  """
  print server, address, `message`
  client_ip, client_port = address
  pkt = fxdns.packet.unpack(message)
  print str(pkt)
  if not pkt.is_valid_query():
    return

  #ans = fxdns.packet.to_answer(pkt)
  #query = q.query[0]

  #if 'test' in query.qname.str():
  #  print "TEST"
  return message