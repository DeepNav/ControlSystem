import logging
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

# a web socket server to push data to client


def start_ws_server(ws_clients, port):
    class DataPusher(WebSocket):
        def handleMessage(self):
            pass

        def handleConnected(self):
            logging.info('ws_server: client connected')
            ws_clients.append(self)

        def handleClose(self):
            ws_clients.remove(self)
            logging.info('ws_server: client closed')

    server = SimpleWebSocketServer('', port, DataPusher)
    server.serveforever()
    logging.info("ws_server started")
