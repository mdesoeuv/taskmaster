import os

# import psutil
import time


def format_uptime(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


def get_process_uptime(pid):
    # Get the system boot time
    with open("/proc/stat") as f:
        for line in f:
            if line.startswith("btime"):
                boot_time = int(line.strip().split()[1])
                break

    # Get the clock ticks per second
    clock_ticks_per_second = os.sysconf(os.sysconf_names["SC_CLK_TCK"])

    # Get the process start time in clock ticks since system boot
    with open(f"/proc/{pid}/stat") as f:
        start_time_ticks = int(f.readline().split()[21])

    # Convert start time to seconds since system boot
    start_time_seconds = start_time_ticks / clock_ticks_per_second

    # Calculate the process uptime
    process_uptime_seconds = time.time() - (boot_time + start_time_seconds)

    # Format in hh:mm:ss
    formated_uptime = format_uptime(process_uptime_seconds)

    return formated_uptime


# def get_process_name(pid):
#    try:
#        p = psutil.Process(pid)
#        return p.name()
#    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#        return None


def get_process_name(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "r") as f:
            # Cela lit la ligne de commande; pour obtenir juste le nom du processus,
            # vous pouvez diviser par '\x00' et prendre le premier élément
            cmdline = f.read().split("\x00")[0]
        return cmdline
    except FileNotFoundError:
        return None
