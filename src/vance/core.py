from typing import List, Dict, Union, Optional
from .types import Process, ProcessResult
from .policies import SchedulerPolicy
from dataclasses import dataclass
from abc import ABC, abstractmethod

class Clock:
    """ """
    def __init__(self):
        self._time = 0

    @property
    def time(self) -> int:
        """ """
        return self._time

    def tick(self) -> int:
        """Advance the system heartbeat by 1 unit."""
        self._time += 1
        return self._time


class Dispatcher:
    """Represents a dispatcher, for managing context switches of processes"""

    def __init__(self, dispatch_latency: int = 0):

        if dispatch_latency < 0:
            self.dispatch_latency = 0
        else:
            self.dispatch_latency = dispatch_latency
        self.current_switch_remaining = 0
        self.target_process_id: Optional[int] = None

    @property
    def is_currently_switching(self) -> bool:
        """ """
        return self.current_switch_remaining > 0

    def start_switch(self, process_id: int):
        """Begin the overhead period for a new process.

        Args:
          process_id: int:
          process_id: int:
          process_id: int: 

        Returns:

        """
        self.target_process_id = process_id
        self.current_switch_remaining = self.dispatch_latency

    def tick(self):
        """Reduce the overhead timer by 1."""
        if self.current_switch_remaining <= 0:
            raise ValueError(
                "No context switch remaining!"
                "There must be a problem with your dispatcher logic."
            )
        else:
            self.current_switch_remaining -= 1


@dataclass
class TraceEvent:
    """ """
    time: int
    event_type: str  # "ARRIVAL", "SWITCH", "EXEC", "IDLE", "FINISHED"
    pid: int

class Tracer:
    """ """
    def __init__(self):
        self.events: List[TraceEvent] = []
        self._log: List[str] = []

    def record(
        self,
        time: int,
        event_type: str,
        pid: Optional[Union[int, str]] = None,
        msg: str = "",
    ):
        """Records a structured event and a string message simultaneously.

        Args:
          time: int:
          event_type: str:
          pid: Optional[Union[int:
          str: Default value = None)
          msg: str:  (Default value = "")
          time: int:
          event_type: str:
          pid: Optional[Union[int:
          str: Default value = None)
          msg: str:  (Default value = "")
          time: int: 
          event_type: str: 
          pid: Optional[Union[int: 
          str]]:  (Default value = None)
          msg: str:  (Default value = "")

        Returns:

        """
        self.events.append(TraceEvent(time, event_type, pid))
        if msg:
            self._log.append(f"T={time}: {msg}")

    def get_log(self) -> List[str]:
        """ """
        return self._log

    def get_structured_data(self) -> List[TraceEvent]:
        """ """
        return self.events