from myServer import IpServices

PORT = 5353


s = IpServices(handler)
s.add(PORT)
s.idle_loop()



