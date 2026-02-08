from dataclasses import dataclass
@dataclass
class Process:
    pid: int
    burst_time: int
    waiting_time: int | None = None
    turnaround_time: int | None = None
