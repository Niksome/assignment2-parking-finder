import json
import struct
import socket


class RPCError(Exception):
    pass

class TimeoutError(Exception):
    pass


class ParkingRPCClient:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.rpc_id = 0

    def getLots(self):               return self._call("getLots", [])
    def getAvailability(self, lotId): return self._call("getAvailability", [lotId])
    def reserve(self, lotId, plate):  return self._call("reserve", [lotId, plate])
    def cancel(self, lotId, plate):   return self._call("cancel", [lotId, plate])

    def _recv_exact(self, sock, n):
        # keep reading until we have all n bytes
        data = b""
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Socket closed unexpectedly")
            data += chunk
        return data

    def _call(self, method, args):
        self.rpc_id = (self.rpc_id + 1) % 0xFFFFFFFF
        request = {"rpcId": self.rpc_id, "method": method, "args": args}

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5.0)
            sock.connect((self.host, self.port))
            try:
                # send the request
                payload = json.dumps(request).encode("utf-8")
                sock.sendall(struct.pack(">I", len(payload)) + payload)

                # get the response
                header = self._recv_exact(sock, 4)
                length = struct.unpack(">I", header)[0]
                response = json.loads(self._recv_exact(sock, length).decode("utf-8"))
            except socket.timeout:
                raise TimeoutError(f"RPC '{method}' timed out")

        if response.get("error"):
            raise RPCError(response["error"])
        return response["result"]