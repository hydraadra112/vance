from metrics import calculate_turnaround_time, calculate_waiting_time
from base import Process, ProcessResult
from utils import is_sorted_by_arrival

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
    current_time = 0

    for process in processes:
        waiting_time = calculate_waiting_time(process.arrival_time, current_time)
        turnaround_time = calculate_turnaround_time(process.burst_time, waiting_time)
        completion_time = process.arrival_time + turnaround_time

        # Append results
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