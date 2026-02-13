from typing import List, Dict
from policies import SchedulerPolicy

class Clock:
    def __init__(self):
        self._time = 0

    @property
    def time(self) -> int:
        return self._time

    def tick(self) -> int:
        """Advance the system heartbeat by 1 unit."""
        self._time += 1
        return self._time