import logging
import time
import json

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

# a web socket server to push data to client


class WsServer(object):
    def __init__(self, port):
        self.ws_clients = []
        ws_server = self

        class DataPusher(WebSocket):
            def handleMessage(self):
                pass

            def handleConnected(self):
                logging.info('ws_server: client connected')
                ws_server.ws_clients.append(self)

            def handleClose(self):
                ws_server.ws_clients.remove(self)
                logging.info('ws_server: client closed')

        self.server = SimpleWebSocketServer('', port, DataPusher)

    def start_server(self):
        self.server.serveforever()
        logging.info("ws_server started")

    def broadcast(self, msg):
        for client in self.ws_clients:
            msg.update({
                "ts": time.time()
            })
            client.sendMessage(unicode(json.dumps(msg)))
