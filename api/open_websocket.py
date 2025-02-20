import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid

def open_websocket_connection():
  server_address='192.168.0.10:8188'
  client_id=str(uuid.uuid4())

  ws = websocket.WebSocket()
  ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
  return ws, server_address, client_id
