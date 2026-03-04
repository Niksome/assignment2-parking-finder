import socket
import threading
import queue
import json
from parking_state import ParkingState


DEFAULT_CONFIG_PATH = "config.json"

# config keys
CONFIG_HOST = "host"
CONFIG_PORT = "port"
CONFIG_BACKLOG = "backlog"
CONFIG_THREAD_POOL_SIZE = "thread_pool_size"
CONFIG_CONN_QUEUE_SIZE = "conn_queue_size"
CONFIG_LOTS = "lots"
CONFIG_RESERVATION_TTL_SECONDS = "reservation_ttl_seconds"

# command and response tokens
CMD_PING = "PING"
RESP_PONG = "PONG"
CMD_LOTS = "LOTS"
CMD_AVAIL = "AVAIL"
CMD_RESERVE = "RESERVE"
CMD_CANCEL = "CANCEL"
RESP_ERR = "ERR"
RESP_ERR_UNKNOWN_LOT = "ERR UNKNOWN_LOT"

# log/messages
MSG_CONN_QUEUE_FULL = "Connection queue full. Dropping connection."
MSG_SERVER_LISTENING = "Server listening on {host}:{port}"
LOG_CLIENT_ERROR = "Client error:"

# I/O constants
MODE_READ = "r"
MODE_WRITE = "w"
ENCODING_UTF8 = "utf-8"


def load_config(path=DEFAULT_CONFIG_PATH):
    with open(path, MODE_READ) as f:
        return json.load(f)


class ParkingServer:
    def __init__(self, config):
        self.host = config[CONFIG_HOST]
        self.port = config[CONFIG_PORT]
        self.backlog = config.get(CONFIG_BACKLOG, 128)
        self.pool_size = config.get(CONFIG_THREAD_POOL_SIZE, 8)
        self.conn_queue_size = config.get(CONFIG_CONN_QUEUE_SIZE, 100)

        self.state = ParkingState(
            config[CONFIG_LOTS],
            ttl_seconds=config.get(CONFIG_RESERVATION_TTL_SECONDS, 300)
        )

        self.conn_queue = queue.Queue(maxsize=self.conn_queue_size)
        self.workers = []

    def start(self):
        for _ in range(self.pool_size):
            t = threading.Thread(target=self.worker_loop, daemon=True)
            t.start()
            self.workers.append(t)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(self.backlog)
            print(MSG_SERVER_LISTENING.format(host=server.host, port=server.port))

            while True:
                conn, addr = s.accept()
                try:
                    self.conn_queue.put(conn, block=False)
                except queue.Full:
                    print(MSG_CONN_QUEUE_FULL)
                    conn.close()

    def worker_loop(self):
        while True:
            conn = self.conn_queue.get()
            try:
                self.handle_client(conn)
            except Exception as e:
                print(LOG_CLIENT_ERROR, e)
            finally:
                conn.close()

    def handle_client(self, conn):
        rfile = conn.makefile(MODE_READ, encoding=ENCODING_UTF8)
        wfile = conn.makefile(MODE_WRITE, encoding=ENCODING_UTF8)

        for line in rfile:
            line = line.strip()
            if not line:
                continue

            response = self.handle_command(line)

            wfile.write(response + "\n")
            wfile.flush()

    def handle_command(self, line: str) -> str:
        parts = line.split()
        cmd = parts[0].upper()

        try:
            if cmd == CMD_PING:
                return RESP_PONG

            elif cmd == CMD_LOTS:
                lots = self.state.get_lots()
                return json.dumps(lots)
            elif cmd == CMD_AVAIL and len(parts) == 2:
                free = self.state.get_availability(parts[1])
                return str(free)

            elif cmd == CMD_RESERVE and len(parts) == 3:
                return self.state.reserve(parts[1], parts[2])

            elif cmd == CMD_CANCEL and len(parts) == 3:
                return self.state.cancel(parts[1], parts[2])

            else:
                return RESP_ERR

        except KeyError:
            return RESP_ERR_UNKNOWN_LOT
        except Exception:
            return RESP_ERR


if __name__ == "__main__":
    config = load_config()
    server = ParkingServer(config)
    server.start()