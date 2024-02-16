import os
import time


def format_uptime(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


def get_process_name(pid):
    print(f"Getting process name for pid {pid}")
    try:
        with open(f"/proc/{pid}/cmdline", "r") as f:
            # Cela lit la ligne de commande; pour obtenir juste le nom du processus,
            # vous pouvez diviser par '\x00' et prendre le premier élément
            cmdline = f.read().split("\x00")[0]
        return cmdline
    except FileNotFoundError:
        return None
