import fxdns.packet

def handle(server, address, message):
  print "Hello mike !"
  print server, address ,message
  client_ip, client_port = address
  pkt = fxdns.packet.unpack(message)
  if not pkt.is_valid_query():
    return

  ans = pkt.to_answer()
  query = q.query[0]


  if 'test' in query.qname.str():
    print "TEST"

