import socket
import pickle
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class BankingClient:
    def __init__(self, host='127.0.0.1', port=5005):
        self.host = host
        self.port = port

    def send_request(self, request):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host, self.port))
            client.send(pickle.dumps(request))
            response = pickle.loads(client.recv(16384))
            client.close()
            return response
        except ConnectionRefusedError:
            return {"status": "error", "message": "Connection refused. Is the server running?"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
