import sys
import datetime
import glob
import os
import time
from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log
import txthings.resource as resource
import txthings.coap as coap

class TempResource(resource.CoAPResource):
    
    ctemp='/sys/bus/w1/devices/28-0000062b45fa/w1_slave'
    ft_war =-85
    
    def __init__(self):
      resource.CoAPResource.__init__(self)
      self.visible = True
      self.observable = True
      self.notify()

    def getTemp(self):
      lfile=open(self.ctemp, 'r')
      llines=lfile.readlines()
      lfile.close
      if  llines[0].strip()[-3:]=='YES':
         lequals_pos=llines[1].find('t=')
         if lequals_pos!=-1:
            lt_str=llines[1][lequals_pos+2:]
            lt_war=float(lt_str)/1000.0
            if lt_war!=85:
               return lt_war
            else:
               log.msg('Error temperature reading')
               return self.ft_war
         else:
            log.msg('Error temperature reading')
            return self.ft_war
      else:
         log.msg('Error temperature reading')
         return self.ft_war

    def notify(self):
      log.msg('Temperature reading')
      lt_war = self.getTemp()
      if lt_war!=self.ft_war:
         self.ft_war=lt_war
    	   self.updatedState()
         log.msg('Temperature update')
      reactor.callLater(120,self.notify)

    def render_GET(self, request):
      response = coap.Message(code=coap.CONTENT, payload=str(self.ft_war)+'|'+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
      return defer.succeed(response)
      
log.startLogging(sys.stdout)
root = resource.CoAPResource()
Temp = TempResource()
root.putChild('Temp', Temp)
endpoint = resource.Endpoint(root)
reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint))
reactor.run()
