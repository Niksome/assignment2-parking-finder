from parking_state import ParkingState

class RPCServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.state = ParkingState([  # load from config later
            {"id": "LOT-A", "capacity": 50},
            {"id": "LOT-B", "capacity": 30},
        ])

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