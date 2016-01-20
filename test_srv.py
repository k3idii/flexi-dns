import myServer
import logging
logging.basicConfig(level=logging.DEBUG)


def handler(*a):
  print "Handling !", a
  return "PONG"

srv = myServer.IpServices(handler)

srv.add(2001)
srv.idle_loop()




