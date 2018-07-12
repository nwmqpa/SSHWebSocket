"""SSHClient for websocket connection."""
import asyncio
import websockets
import hashlib
import json
import sys

async def handshake():
    """Handshake with the server."""
    global slave
    global password
    async with websockets.connect(sys.argv[1]) as websocket:
        await websocket.send(b"list")
        slave_list = await websocket.recv()
        print("The current slaves are availables :")
        print(" ".join([
            i["name"] if i["name"] is not None else ""
            for i in json.loads(slave_list)
        ]))
        slave = input("Slave name $> ")
        password = hashlib.sha512(input("Password $> ").encode()).hexdigest()
        data = {"command": "echo \"The password is good\"", "slave": slave, "pswd": password}
        await websocket.send(json.dumps(data).encode())
        greeting = await websocket.recv()




async def send_commands():
    """Send a command."""
    global slave
    global password
    async with websockets.connect(sys.argv[1]) as websocket:
        while True:
            command = input(" $> ")
            data = {"command": command, "slave": slave, "pswd": password}
            await websocket.send(json.dumps(data).encode())
            greeting = await websocket.recv()
            try:
                returned = json.loads(greeting)
            except json.decoder.JSONDecodeError:
                print("Unkown JSON")
            else:
                print(returned["stdout"][:-1])
                print(returned["stderr"][:-1])

def main():
    global slave
    while True:
        asyncio.get_event_loop().run_until_complete(handshake())
        try:
            asyncio.get_event_loop().run_until_complete(send_commands())
        except EOFError:
            print(f"Exiting {slave}")

if __name__ == "__main__":
    try:
        main()
    except EOFError:
        print("Exiting...")
