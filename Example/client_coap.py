import sys
from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log
import txthings.coap as coap
import txthings.resource as resource
from websocket import create_connection
from ipaddress import ip_address

class Agent():

    def __init__(self, protocol):
        self.protocol = protocol
        reactor.callLater(1, self.requestResource)

    def requestResource(self):
        request = coap.Message(code=coap.GET)
        request.opt.uri_path = ('Temp',)
        request.opt.observe = 0
        request.remote = (ip_address("127.0.0.1"), 5683)
        d = protocol.request(request, observeCallback=self.printLaterResponse)
        d.addCallback(self.printResponse)
        d.addErrback(self.noResponse)

    def printResponse(self, response):
        ws = create_connection("ws://localhost:9090/ws")
        ws.send(response.payload)
        result =  ws.recv()
        log.msg("Connected to WebSocket Server: '%s'" % result)
        log.msg("New value send: "+response.payload)
        ws.close()
        #reactor.stop()
    
    def printLaterResponse(self, response):
        ws = create_connection("ws://localhost:9090/ws")
        ws.send(response.payload)
        result =  ws.recv()
        log.msg("Received from WebSocket Server: '%s'" % result)
        ws.close()

    def noResponse(self, failure):
        log.msg('Message failure')
        reactor.stop()

log.startLogging(sys.stdout)

endpoint = resource.Endpoint(None)
protocol = coap.Coap(endpoint)
client = Agent(protocol)

reactor.listenUDP(61616, protocol)
reactor.run()
