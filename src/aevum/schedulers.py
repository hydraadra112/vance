from metrics import calculate_turnaround_time, calculate_waiting_time, calculate_completion_time
from base import Process, ProcessResult
from utils import is_sorted_by_arrival, is_sorted_by_burst, sort_processes_by_arrival, sort_processes_by_burst

def run_fcfs_simulation(processes: list[Process]) -> dict:
    """
    Executes FCFS scheduling and returns a dictionary of results.

    Args:
        processes(Process): A list of the class Process.

    Returns:
        dict: A dictionary containing the individual results, and its averages.
    """
    if not processes:
        raise ValueError("Process list is empty!")

    # Check if sorted
    if not is_sorted_by_arrival(processes):
        raise ValueError(
            "FCFS requires processes to be sorted by arrival time. "
            "Please use 'aevum.utils.sort_processes_by_arrival()' before passing the list."
        )

    process_results: list[ProcessResult] = []
    current_time = 0 # Initial completion time

    for process in processes:
        waiting_time = max(current_time, process.arrival_time)
        completion_time = current_time + process.burst_time
        turnaround_time = completion_time - process.arrival_time

        # Save results
        process_results.append(ProcessResult(
            process=process,
            waiting_time=waiting_time,
            turnaround_time=turnaround_time,
            completion_time=completion_time
        ))
        
        current_time = completion_time

    avg_wait = sum(r.waiting_time for r in process_results) / len(process_results)
    avg_tat = sum(r.turnaround_time for r in process_results) / len(process_results)

    # Construct Output Dictionary
    return {
        "individual_results": [
            {
                "pid": r.process.pid,
                "wait": r.waiting_time,
                "turnaround": r.turnaround_time,
                "completion": r.completion_time
            } for r in process_results
        ],
        "averages": {
            "avg_waiting_time": round(avg_wait, 2),
            "avg_turnaround_time": round(avg_tat, 2)
        }
    }

def run_sjf_simulation(processes: list[Process]) -> dict:
    """
    Executes Shortest Job First (SJF) scheduling and returns a dictionary of results.

    Args:
        processes(Process): A list of the class Process.

    Returns:
        dict: A dictionary containing the individual results, and its averages.
    """
    if not processes:
        raise ValueError("Process list is empty!")

    # Check if sorted
    if not is_sorted_by_arrival(processes):
        raise ValueError(
            "SJF requires processes to be sorted by arrival time. "
            "Please use 'aevum.utils.sort_processes_by_arrival()' before passing the list."
        )
    
    process_results: list[ProcessResult] = []
    ready_processes: list[ProcessResult] = []
    current_time = 0

    # We sort by burst time on lists that have arrived
    while processes or ready_processes:
        while processes and processes[0].arrival_time <= current_time:
            ready_processes.append(processes.pop(0))

        if not ready_processes:
            current_time = processes[0].arrival_time
            continue

        current_process = min(ready_processes, key=lambda p: p.burst_time)
        ready_processes.remove(current_process)

        waiting_time = max(current_time, current_process.arrival_time)
        completion_time = current_time + current_process.burst_time
        turnaround_time = completion_time - current_process.arrival_time

        process_results.append(ProcessResult(
            process=current_process,
            waiting_time=waiting_time,
            turnaround_time=turnaround_time,
            completion_time=completion_time
        ))

        current_time = completion_time
    
    avg_wait = sum(r.waiting_time for r in process_results) / len(process_results)
    avg_tat = sum(r.turnaround_time for r in process_results) / len(process_results)

    return {
        "individual_results": [
            {
                "pid": r.process.pid,
                "wait": r.waiting_time,
                "turnaround": r.turnaround_time,
                "completion": r.completion_time
            } for r in process_results
        ],
        "averages": {
            "avg_waiting_time": round(avg_wait, 2),
            "avg_turnaround_time": round(avg_tat, 2)
        }
    }














