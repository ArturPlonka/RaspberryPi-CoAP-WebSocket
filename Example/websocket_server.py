import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import uuid


global fvar
fvar = ""

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    loader = tornado.template.Loader(".")
    self.write(loader.load("index.html").generate())

class WSHandler(tornado.websocket.WebSocketHandler):
  connections = set()
  def check_origin(self, origin):
    return True

  def open(self):
    self.connections.add(self)
    self.id = uuid.uuid4()
    print 'Connection opened '+str(self.id)
    self.write_message(globals()["fvar"])

  def on_message(self, message):
    [con.write_message(message) for con in self.connections]
    globals()["fvar"] = message
    print 'New value received: '+fvar

  def on_close(self):
    self.connections.remove(self)
    print 'Connection closed '+str(self.id)

application = tornado.web.Application([
  (r'/ws', WSHandler),
  (r'/', MainHandler),
  (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./resources"}),
])

if __name__ == "__main__":
  print 'Tornado started'
  application.listen(9090)
  tornado.ioloop.IOLoop.instance().start()
