import json
import struct
import socket
import threading


class RPCServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(5)
        # spin up a new thread for each client that connects
        while True:
            conn, _ = s.accept()
            threading.Thread(target=self.handle_client, args=(conn,)).start()

    def _recv_exact(self, sock, n):
        # keep reading until we have all n bytes
        data = b""
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Socket closed unexpectedly")
            data += chunk
        return data

    def handle_client(self, conn):
        try:
            # read the request
            length = struct.unpack(">I", self._recv_exact(conn, 4))[0]
            request = json.loads(self._recv_exact(conn, length).decode("utf-8"))

            # run the method, catch any errors and send them back
            try:
                result = self.dispatch(request["method"], request["args"])
                response = {"rpcId": request["rpcId"], "result": result, "error": None}
            except Exception as e:
                response = {"rpcId": request["rpcId"], "result": None, "error": str(e)}

            # send the response
            payload = json.dumps(response).encode("utf-8")
            conn.sendall(struct.pack(">I", len(payload)) + payload)
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            conn.close()

    def dispatch(self, method, args):
        # route to the right method (mocks for now, swap in real logic later)
        if method == "getLots":
            return [{"id": "LOT-A", "capacity": 50, "occupied": 10, "free": 40}]
        elif method == "getAvailability":
            return 40
        elif method == "reserve":
            return True
        elif method == "cancel":
            return True
        else:
            raise ValueError(f"Unknown method: {method}")