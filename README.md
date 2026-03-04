CECS 327 Campus Smart Parking Finder
Group members:

Andrej Ermoshkin

Ashley Celis


Fortune Meya



How to run:
Step 0: Setup

Create a virtual environment: python -m venv .venv
Activate it:

On Windows: .venv\Scripts\activate
On Linux/macOS: source .venv/bin/activate

Install dependencies: pip install -r requirements.txt

Step 1: Start the Parking Server
Command: python parking_server.py

Step 2: Start the Dispatcher (RPC) Server
Command: python parking_dispatcher_server.py

Step 3: Run the Client
Command: python parking_client.py

Step 4: Run the Sensor Simulator
Command: python sensorsimulator

Step 5: Run the Subscriber Client
Command: python SubscriberClient


