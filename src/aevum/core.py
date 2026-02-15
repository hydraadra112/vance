from typing import List, Dict, Optional
from aevum.types import Process, ProcessResult
from aevum.policies import SchedulerPolicy

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

class Dispatcher:
    """ Represents a dispatcher, for managing context switches of processes """
    def __init__(self, dispatch_latency: int = 0):

        if dispatch_latency < 0:
            self.dispatch_latency = 0
        else:
            self.dispatch_latency = dispatch_latency
        self.current_switch_remaining = 0
        self.target_process_id: Optional[int] = None

    @property
    def is_currently_switching(self) -> bool:
        return self.current_switch_remaining > 0

    def start_switch(self, process_id: int):
        """Begin the overhead period for a new process."""
        self.target_process_id = process_id
        self.current_switch_remaining = self.dispatch_latency

    def tick(self):
        """Reduce the overhead timer by 1."""
        if self.current_switch_remaining <= 0:
            raise ValueError("No context switch remaining!"
                             "There must be a problem with your dispatcher logic.")
        else:    
            self.current_switch_remaining -= 1

class SimulationEngine:
    def __init__(self, policy: SchedulerPolicy, dispatch_latency: int = 0):
        self.policy = policy
        self.clock = Clock()
        self.dispatcher = Dispatcher()
        self.dispatcher = Dispatcher(dispatch_latency=dispatch_latency)
        self.results: List[ProcessResult] = []
        self.trace_log: List[str] = []
        
    def run(self, processes: List[Process]) -> Dict:
        """
        The main logic for process execution with policies for queue and process handling

        Args:
            processes(list[Process]): A list of processes that you wish to execute

        Returns:
            dict: A dictionary formatted output
        """
        if not processes:
            raise ValueError("Process list is empty")
        
        # 1. Setup
        # We internally sort our processes by arrival time to ensure that the first one to arrive will
        # be the one to picked out
        incoming = sorted(processes, key=lambda p: (p.arrival_time, p.pid))
 
        ready_queue: List[Process] = []
        remaining_times = {p.pid: p.burst_time for p in incoming}
        
        current_job_runtime = 0 # Tracks how long current job has been running (for RR)

        next_process: Optional[Process] = None
        current_process: Optional[Process] = None

        # 2. The Loop
        while incoming or ready_queue or current_process or self.dispatcher.is_currently_switching:
            
            # A. Handle Arrivals
            # We check arrivals before asking the policy so the policy sees everyone
            print("A. CHECKING ARRIVALS!")
            while incoming and incoming[0].arrival_time <= self.clock.time:
                new_proc = incoming.pop(0)
                ready_queue.append(new_proc)
                self.trace_log.append(f"T={self.clock.time}: Process {new_proc.pid} arrived.")

                print(f"T={self.clock.time}: Process {new_proc.pid} arrived.")

            # Condition to not change process during a context switch
            print(f"Checking if dispatchet is currently switching: {self.dispatcher.is_currently_switching}")
            if not self.dispatcher.is_currently_switching:
                # B. Ask Policy for Decision (Policy Responsibility)
                # We pass the mutable ready_queue so the policy can pop/append if needed

                print("Getting new process via policy get_next_process")
                next_process = self.policy.get_next_process(
                    ready_queue, 
                    current_process, 
                    current_job_runtime, 
                    remaining_times
                )
            
                # C. Detect & Handle Context Switch
                print(f"Checking if next process != current process: {next_process != current_process}")
                if next_process != current_process:

                    print(f"Checking if self.dispatcher.dispatch_latency > 0: {self.dispatcher.dispatch_latency > 0}")
                    if self.dispatcher.dispatch_latency > 0:
                        self.dispatcher.start_switch(next_process.pid if next_process else None)
                        self.trace_log.append(f"T={self.clock.time}: STARTING SWITCH to P{next_process.pid if next_process else 'Idle'}")

                        print(f"T={self.clock.time}: STARTING SWITCH to P{next_process.pid if next_process else 'Idle'}")

                    else:
                        current_process = next_process
                        current_job_runtime = 0

            # D. Execute System Tick
            if self.dispatcher.is_currently_switching:
                # CPU is busy swapping context, no work done on processes!
                self.dispatcher.tick()
                print("Dispatcher Tick!")
                self.trace_log.append(f"T={self.clock.time}: Dispatcher busy...")
                print(f"T={self.clock.time}: Dispatcher busy...")

                # Automatically go to next process
                # if latency is <= 0 
                if not self.dispatcher.is_currently_switching:
                    current_process = next_process
                    current_job_runtime = 0
                    pid_str = current_process.pid if current_process else 'Idle'
                    self.trace_log.append(f"T={self.clock.time}: Switch complete. P{pid_str} is now on CPU.")

                    print(f"T={self.clock.time}: Switch complete. P{pid_str} is now on CPU.")

            elif current_process:
                print("Decrement remaining time of current process")
                remaining_times[current_process.pid] -= 1
                current_job_runtime += 1
                
                print("Check completion")
                # Check Completion
                if remaining_times[current_process.pid] == 0:
                    self._record_completion(current_process)
                    current_process = None # Job done, CPU is free
                    current_job_runtime = 0
            else:
                self.trace_log.append(f"T={self.clock.time}: CPU Idle.")
            
            print(f"T={self.clock.time}: CLOCK TICK!")
            self.clock.tick()

        return self._get_output()

    def _record_completion(self, process: Process):
        """Helper to calculate metrics when a process finishes."""
        
        completion_time = self.clock.time + 1 # +1 because we finish at end of tick
        turnaround = completion_time - process.arrival_time
        wait = turnaround - process.burst_time
        
        self.results.append(ProcessResult(
            process, wait, turnaround, completion_time
        ))
        self.trace_log.append(f"T={completion_time}: Process {process.pid} FINISHED.")

    def _get_output(self) -> Dict:
        """Standardized dictionary output."""
        avg_wait = sum(r.waiting_time for r in self.results) / len(self.results)
        avg_tat = sum(r.turnaround_time for r in self.results) / len(self.results)
        
        return {
            "individual_results": [
                {
                    "pid": r.process.pid,
                    "wait": r.waiting_time,
                    "turnaround": r.turnaround_time,
                    "completion": r.completion_time
                } for r in self.results
            ],
            "averages": {
                "avg_waiting_time": round(avg_wait, 2),
                "avg_turnaround_time": round(avg_tat, 2)
            },
            "trace": self.trace_log
        }