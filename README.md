# CECS 327 Campus Smart Parking Finder
Group members:

Andrej Ermoshkin

Ashley Celis


Fortune Meya



## How to run:
### Step 0: Setup

#### Virtual environment
Create a virtual environment: `python -m venv .venv`
Activate it:
- On Windows: `.venv\Scripts\activate`
- On Linux/macOS: `source .venv/bin/activate`

No packages were used.

#### Configuration
This is the `config.json` for the dispatcher:
```
{
  "host": "127.0.0.1",
  "port": 5001,
  "backlog": 128,
  "thread_pool_size": 16,
  "conn_queue_size": 256,
  "reservation_ttl_seconds": 300,
  "lots": [
    {"id": "A", "capacity": 50},
    {"id": "B", "capacity": 30},
    {"id": "C", "capacity": 25}
  ]
}
```
You can adjust:
- `host` to change the ip the server is running on
- `port` to change the port where the TCP connection is open
- `thread_pool_size` to change the amount of worker threads
- `conn_queue_size` to change the amount of TCP connections accepted
- `reservation_ttl_seconds` to change the time you are allowed to reserve a parking spot
- lots:
  - you can add or remove parking lots
  - adjust the id of a parking lot
  - adjust the amount of parking spots a parking lot has

### Step 1: Start the Parking Server
Command: python parking_server.py

### Step 2: Start the Dispatcher (RPC) Server
Command: python parking_dispatcher_server.py

### Step 3: Run the Client
Command: python parking_client.py

### Step 4: Run the Sensor Simulator
Command: python sensorsimulator

### Step 5: Run the Subscriber Client
Command: python SubscriberClient



