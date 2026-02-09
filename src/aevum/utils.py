from base import Process

def is_sorted_by_arrival(processes: list[Process]) -> bool:
    """Check if processes are ordered by arrival time."""
    return all(processes[i].arrival_time <= processes[i+1].arrival_time 
               for i in range(len(processes) - 1))

def sort_processes_by_arrival(processes: list[Process]) -> list[Process]:
    """Returns a new list sorted by arrival time."""
    return sorted(processes, key=lambda p: p.arrival_time)