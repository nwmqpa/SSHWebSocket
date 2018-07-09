"""WebSocket SSHServer."""
import websocket
import json
import uuid
import thread
import time
import subprocess
import os


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

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = SSHServer("ws://192.168.1.23:8080")
    ws.run_forever()
