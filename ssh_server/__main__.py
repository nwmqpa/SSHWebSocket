"""WebSocket SSHServer."""
import websocket
import json
import uuid
import thread
import time
import subprocess
import os
from urllib.request import urlopen, urlcleanup

"""Current version of the program."""
VERSION = "0.0.1"

"""Startup CWD of the program."""
STARTUP_CWD = os.getcwd()

"""Online file containing the newest version number."""
VERSION_FILE = (
    "https://raw.githubusercontent.com/nwmqpa/SSHWebSocket/master/ssh_server/version"
)

"""Online file containing the updated source code."""
SOURCE_FILE = (
    "https://raw.githubusercontent.com/nwmqpa/SSHWebSocket/master/ssh_server/__main__.py"
)


class SSHServer(websocket.WebSocketApp):
    """Class for defining a websocket SSHServer."""

    def __init__(*args, **kwargs):
        """Initialize the object."""
        super(SSHServer, self).__init__(*args, **kwargs)

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
                    "name": os.uname()[1]
                    })
                ws.send(con_infos)
            run()


def check_update():
    """Check the update of the current script."""
    data = urlopen(VERSION_FILE)
    if VERSION != data.readline()[:-1].decode():
        print("Update spotted, updating...")
        source = urlopen(SOURCE_FILE)
        with open(sys.argv[0] + "/__main__.py", "w") as this_file:
            for line in source:
                this_file.write(line.decode())
        args = sys.argv[:]
        args.insert(0, sys.executable)
        os.chdir(STARTUP_CWD)
        os.execv(sys.executable, args)
    else:
        print("No update available.")

if __name__ == "__main__":
    urlcleanup()
    try:
        check_update()
    except:
        print("Can't connect to update server.")
    websocket.enableTrace(True)
    ws = SSHServer("ws://0.0.0.0:8080")
    ws.run_forever()
