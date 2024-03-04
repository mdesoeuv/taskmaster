def get_process_name(pid):
    print(f"Getting process name for pid {pid}")
    try:
        with open(f"/proc/{pid}/cmdline", "r") as f:
            # Split by '\x00' and take the first element to process name
            cmdline = f.read().split("\x00")[0]
        return cmdline
    except FileNotFoundError:
        return None
