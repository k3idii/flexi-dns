import myServer

def handler():
  print "Handling !"

srv = myServer.IpServices(handler)

srv.add(2001)
srv.start()

while True:
  import time
  time.sleep(1)
  srv.stop()

srv.wait_for_all()