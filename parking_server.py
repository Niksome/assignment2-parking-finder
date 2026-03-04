import json
import struct
import socket
import threading
from parking_state import ParkingState


class RPCServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.state = ParkingState([
            {"id": "LOT-A", "capacity": 50},
            {"id": "LOT-B", "capacity": 30},
        ])

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(5)
        while True:
            conn, _ = s.accept()
            threading.Thread(target=self.handle_client, args=(conn,)).start()

    def _recv_exact(self, sock, n):
        data = b""
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Socket closed unexpectedly")
            data += chunk
        return data

    def handle_client(self, conn):
        try:
            length = struct.unpack(">I", self._recv_exact(conn, 4))[0]
            request = json.loads(self._recv_exact(conn, length).decode("utf-8"))
            try:
                result = self.dispatch(request["method"], request["args"])
                response = {"rpcId": request["rpcId"], "result": result, "error": None}
            except Exception as e:
                response = {"rpcId": request["rpcId"], "result": None, "error": str(e)}
            payload = json.dumps(response).encode("utf-8")
            conn.sendall(struct.pack(">I", len(payload)) + payload)
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            conn.close()

    def dispatch(self, method, args):
        if method == "getLots":
            return self.state.get_lots()
        elif method == "getAvailability":
            return self.state.get_availability(args[0])
        elif method == "reserve":
            return self.state.reserve(args[0], args[1])
        elif method == "cancel":
            return self.state.cancel(args[0], args[1])
        else:
            raise ValueError(f"Unknown method: {method}")