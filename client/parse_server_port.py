import argparse


def parse_server_port() -> int:
    parser = argparse.ArgumentParser(description="Process taskmaster options.")
    parser.add_argument(
        "-p",
        dest="server_port",
        type=str,
        required=True,
        help="Specify the port to use for the server.",
    )
    args = parser.parse_args()
    port: int = int(args.server_port)
    return port
