"""WebSocket SSHServer."""
import websocket
import json
import uuid
import _thread
import time
import subprocess
import os
import sys
import hashlib

def on_message(ws, message):
    """Load on receiving a message."""
    print(message)
    process = subprocess.Popen(
        message,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.wait()
    out, err = process.communicate()
    errcode = process.returncode
    ws.send(json.dumps({
        "stdout": out.decode(),
        "stderr": err.decode(),
        "code": errcode
    }))


def on_error(ws, error):
    """Load on getting an error."""
    print(error)


def on_close(ws):
    """Load on getting a close from master socket."""
    print("### closed ###")


def on_open(ws):
    """Load on opening a connection to the master server."""
    def run(*args):
        con_infos = json.dumps({
            "type": "slave",
            "name": os.uname()[1],
            "pswd": hashlib.sha512(sys.argv[2].encode()).hexdigest()
            })
        ws.send(con_infos)
    run()


class SSHServer(websocket.WebSocketApp):
    """Class for defining a websocket SSHServer."""

    def __init__(self, *args, **kwargs):
        """Initialize the object."""
        super(SSHServer, self).__init__(
            *args,
            on_close=on_close,
            on_error=on_error,
            on_message=on_message,
            **kwargs
        )
        self.on_open = on_open

def main():
    websocket.enableTrace(True)
    ws = SSHServer(sys.argv[1])
    ws.on_open = on_open
    ws.run_forever()

if __name__ == "__main__":
    main()