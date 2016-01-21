import logging
logging.basicConfig(level=logging.DEBUG)

from myServer import IpServices
from ugly_dns import handle


PORT = 1053


s = IpServices(handle)
s.add(PORT)
s.idle_loop()



