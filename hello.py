# -*- coding: utf-8 -

import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
#import urllib
import tornado.options
import os
from proxyS import ProxyS

class Index1Handler(tornado.web.RequestHandler):
    def get(self):
        self.render("index2.html")

class Index2Handler(tornado.web.RequestHandler):
    def get(self):
        self.render("index1.html")
                
class StatusHandler(tornado.websocket.WebSocketHandler):
    
    def check_origin(self, origin):
        #parsed_origin = urllib.parse.urlparse(origin)
        #return parsed_origin.netloc.endswith(".jrj.com.cn")
        return True
    
    def open(self):        
        self.conn = self.application.proxys.getConn()

    def on_close(self):
        self.conn.unregister(self)
                  
    def on_message(self,message):                                                                                   
        self.conn.sendMsg(self, message)                
               
    def callback(self,fs):
        self.write_message(fs)
                        
class Application(tornado.web.Application):                          
    def __init__(self):         
        self.proxys = ProxyS(50,'117.121.12.239',8601) 
                                   
        handlers = [
            (r'/', Index1Handler),
            (r'/2', Index2Handler),
            (r'/websocket', StatusHandler)
        ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )

        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()