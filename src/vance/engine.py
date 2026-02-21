from .types import Process
from .policies import SchedulerPolicy
from typing import List, Dict, Optional
from .types import Process, ProcessResult
from .policies import SchedulerPolicy
from abc import ABC, abstractmethod
from .core import Clock, Tracer, Dispatcher

class BaseEngine(ABC):
    """
    The base engine for creating custom engines of various needs for CPU scheduling. 
    """
    def __init__(self, dispatch_latency: int = 0):
        self.clock = Clock()
        self.tracer = Tracer()
        self.dispatcher = Dispatcher(dispatch_latency=dispatch_latency)
        self.results: List[ProcessResult] = []
        self.total_idle_time = 0
        self.total_switch_time = 0

    @abstractmethod
    def run(self, processes: List[Process]) -> Dict:
        """The core execution loop. Must be implemented by subclasses."""
        pass

    def _record_completion(self, process: Process, finish_time: int) -> None:
        """ Calculates turnaround and wait time, and saves it in self.results """
        turnaround = finish_time - process.arrival_time
        wait = turnaround - process.burst_time
        self.results.append(ProcessResult(process, wait, turnaround, finish_time))

    def _get_output(self, total_burst: int) -> Dict:
        total_time = self.clock.time
        n_results = len(self.results)
        
        # Guard against zero-division if results are empty
        if not self.results:
            avg_wait = 0
            avg_tat = 0
        else:
            avg_wait = sum(r.waiting_time for r in self.results) / n_results
            avg_tat = sum(r.turnaround_time for r in self.results) / n_results


        if total_time > 0:
            utilization = (total_burst / total_time) * 100
        else:
            utilization = 0

        if (total_burst + self.total_switch_time) > 0:
            efficiency = (total_burst / (total_burst + self.total_switch_time)) * 100
        else:
            efficiency = 0

        return {
            "individual_results": [
                {
                    "pid": r.process.pid,
                    "arrival": r.process.arrival_time,
                    "burst": r.process.burst_time,
                    "wait": r.waiting_time,
                    "turnaround": r.turnaround_time,
                    "completion": r.completion_time,
                }
                for r in self.results
            ],
            "averages": {
                "avg_waiting_time": round(avg_wait, 2),
                "avg_turnaround_time": round(avg_tat, 2),
                "cpu_utilization": f"{utilization:.1f}%",
                "hardware_efficiency": f"{efficiency:.1f}%",
            },
            "structured_trace": self.tracer.get_structured_data(),
            "total_time": total_time,
        }

class BasicEngine(BaseEngine):
    """
    A single-queue simulation engine suitable for basic 
    algorithms like FCFS, SJF, RR, and standard Priority Scheduling.
    """
    def __init__(self, policy: SchedulerPolicy, dispatch_latency: int = 0):
        # Call the BaseEngine constructor to setup Clock, Tracer, etc.
        super().__init__(dispatch_latency=dispatch_latency)
        self.policy = policy

    def run(self, processes: list[Process]) -> dict:        
        incoming = sorted(processes, key=lambda p: (p.arrival_time, p.pid))
        ready_queue: list[Process] = []
        remaining_times = {p.pid: p.burst_time for p in incoming}
        
        current_job_runtime = 0
        next_process: Optional[Process] = None
        current_process: Optional[Process] = None

        while (
            incoming
            or ready_queue
            or current_process
            or self.dispatcher.is_currently_switching
        ):
            # 1. Handle Arrivals (At the start of the tick)
            while incoming and incoming[0].arrival_time <= self.clock.time:
                new_proc = incoming.pop(0)
                ready_queue.append(new_proc)
                self.tracer.record(
                    self.clock.time,
                    "ARRIVAL",
                    new_proc.pid,
                    f"Process {new_proc.pid} arrived.",
                )

            # 2. Decision Logic
            # We check if we need to switch even if current_process just finished
            if not self.dispatcher.is_currently_switching:
                potential_next = self.policy.get_next_process(
                    ready_queue, current_process, current_job_runtime, remaining_times
                )

                if potential_next != current_process:
                    if self.dispatcher.dispatch_latency > 0:
                        self.dispatcher.start_switch(
                            potential_next.pid if potential_next else None
                        )
                        next_process = potential_next
                        # Note: We don't clear current_process yet; it's being swapped out
                        self.tracer.record(
                            self.clock.time,
                            "SWITCH_START",
                            next_process.pid if next_process else "Idle",
                            f"STARTING SWITCH to P{next_process.pid if next_process else 'Idle'}",
                        )
                    else:
                        current_process = potential_next
                        current_job_runtime = 0

            # 3. Execution Phase
            if self.dispatcher.is_currently_switching:
                self.total_switch_time += 1
                self.tracer.record(
                    self.clock.time,
                    "SWITCH",
                    next_process.pid if next_process else "Idle",
                    "Dispatcher busy...",
                )
                self.dispatcher.tick()
                if not self.dispatcher.is_currently_switching:
                    current_process = next_process
                    current_job_runtime = 0

            elif current_process:
                self.tracer.record(self.clock.time, "EXEC", current_process.pid)
                # Actual work happens here
                remaining_times[current_process.pid] -= 1
                current_job_runtime += 1

                # Check Completion AFTER work is done
                if remaining_times[current_process.pid] == 0:
                    # Clock advances at the end of the loop,
                    # so completion is current_time + 1
                    self._record_completion(current_process, self.clock.time + 1)
                    current_process = None
                    current_job_runtime = 0
            else:
                self.total_idle_time += 1
                self.tracer.record(self.clock.time, "IDLE", msg="CPU Idle.")

            self.clock.tick()

        return self._get_output(sum(p.burst_time for p in processes))