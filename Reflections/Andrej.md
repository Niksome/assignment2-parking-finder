# Reflection – Andrej Ermoshkin

## What did you implement?

- setting up the repository
- ```config.json```
- ```parking_dispatcher_server.py```
  - implemented a dispatcher/worker architecture using a bounded thread pool and connection queue
  - main thread accepts TCP connections -> dispatches them to worker threads
  - each worker handles commands and interacts with the same `ParkingState`instance
- ```parking_state.py```
  - implemented the in-memory parking lot model with per-lot locks to ensure thread safety under concurrent access
  - supports reservation expiration
  - The ```reserve()``` function guarantees no overbooking by performing the capacity check and update under the same lock
- So in total I did Part A (Multithreaded Parking Server)


## Bug fixes

- minor bugs while implementing Part A
- for example in ```parking_state.py``` in the ```get_lot()``` function I called the function I was implementing by accident


## One design change

I considered using a single global lock for all parking lots, but changed the design to use per-lot locks instead. This improves concurrency because operations on different lots can proceed in parallel without blocking each other, while still preventing race conditions within each individual lot.