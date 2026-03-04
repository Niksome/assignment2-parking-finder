from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import threading
import time

# Change this to adjust the reservation time. It is given in seconds
RESERVATION_TIME = 300

# result codes of commands
OK = "OK"
ERR = "ERR"
EXISTS = "EXISTS"
FULL = "FULL"
NOT_FOUND = "NOT_FOUND"

# error message templates
ERR_TTL = "ttl_seconds must be > 0"
ERR_CFG_FORMAT = "Each lot config must be a dict like {'id': 'A', 'capacity': 50}"
ERR_CFG_KEYS = "Each lot must have keys: 'id' and 'capacity'"
ERR_EMPTY_LOT_ID = "lot id cannot be empty"
ERR_CAPACITY = "capacity must be >= 0 for lot {lot_id}"
ERR_DUPLICATE_LOT = "duplicate lot id: {lot_id}"

# keys
LOT_ID_KEY = "id"
CAPACITY_KEY = "capacity"
OCCUPIED_KEY = "occupied"
FREE_KEY = "free"


@dataclass
class Lot:
    lot_id: str
    capacity: int
    reservations: Dict[str, float] = field(default_factory=dict)


class ParkingState:
    def __init__(self, lots: List[dict], ttl_seconds: int = RESERVATION_TIME) -> None:
        if ttl_seconds <= 0:
            raise ValueError(ERR_TTL)

        self.ttl_seconds = int(ttl_seconds)
        self._lots: Dict[str, Lot] = {}
        self._locks: Dict[str, threading.Lock] = {}

        for cfg in lots:
            if not isinstance(cfg, dict):
                raise ValueError(ERR_CFG_FORMAT)
            if LOT_ID_KEY not in cfg or CAPACITY_KEY not in cfg:
                raise ValueError(ERR_CFG_KEYS)

            lot_id = str(cfg[LOT_ID_KEY]).strip()
            if not lot_id:
                raise ValueError(ERR_EMPTY_LOT_ID)

            capacity = int(cfg[CAPACITY_KEY])
            if capacity < 0:
                raise ValueError(ERR_CAPACITY.format(lot_id=lot_id))
            if lot_id in self._lots:
                raise ValueError(ERR_DUPLICATE_LOT.format(lot_id=lot_id))

            self._lots[lot_id] = Lot(lot_id=lot_id, capacity=capacity)
            self._locks[lot_id] = threading.Lock()

    def _now(self) -> float:
        return time.time()

    def _get_lot(self, lot_id: str) -> Lot:
        lot_id = str(lot_id).strip()
        lot = self._lots.get(lot_id)
        if lot is None:
            raise KeyError(lot_id)
        return lot

    def _cleanup_expired_locked(self, lot: Lot, now: Optional[float] = None) -> int:
        if now is None:
            now = self._now()

        expired = [plate for plate, exp in lot.reservations.items() if exp <= now]
        for plate in expired:
            del lot.reservations[plate]
        return len(expired)

    def get_lots(self) -> List[dict]:
        now = self._now()
        result: List[dict] = []

        for lot_id in sorted(self._lots.keys()):
            lot = self._lots[lot_id]
            lock = self._locks[lot.lot_id]

            with lock:
                self._cleanup_expired_locked(lot, now=now)

                occupied = len(lot.reservations)
                free = lot.capacity - occupied
                result.append(
                    {
                    LOT_ID_KEY: lot.lot_id,
                    CAPACITY_KEY: lot.capacity,
                    OCCUPIED_KEY: occupied,
                    FREE_KEY: free,
                    }
                )
        return result

    def get_availability(self, lot_id: str) -> int:
        lot = self._get_lot(lot_id)
        lock = self._locks[lot.lot_id]
        now = self._now()

        with lock:
            self._cleanup_expired_locked(lot, now=now)

            active = len(lot.reservations)
            return lot.capacity - active

    def reserve(self, lot_id: str, plate: str) -> str:
        plate = str(plate).strip()
        if not plate:
            return ERR

        lot = self._get_lot(lot_id)
        lock = self._locks[lot.lot_id]
        now = self._now()

        with lock:
            self._cleanup_expired_locked(lot, now=now)

            if plate in lot.reservations:
                return EXISTS

            active = len(lot.reservations)
            if active >= lot.capacity:
                return FULL

            lot.reservations[plate] = now + self.ttl_seconds
            return OK

    def cancel(self, lot_id: str, plate: str) -> str:
        plate = str(plate).strip()
        if not plate:
            return ERR
        
        lot = self._get_lot(lot_id)
        lock = self._locks[lot.lot_id]
        now = self._now()

        with lock:
            self._cleanup_expired_locked(lot, now=now)

            if plate not in lot.reservations:
                return NOT_FOUND
            
            del lot.reservations[plate]
            return OK
