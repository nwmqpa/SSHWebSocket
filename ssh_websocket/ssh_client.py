"""SSHClient for websocket connection."""
import asyncio
import websockets
import json

async def hello():
    """Send a command."""
    async with websockets.connect(
            'ws://nwmqpa.com:8080') as websocket:
        await websocket.send(b"list")
        slave_list = await websocket.recv()
        print(" ".join([
            i["name"] if i["name"] is not None else ""
            for i in json.loads(slave_list)
        ]))
        slave = input("What slave ? ")
        command = input("What's your command ")

        data = {"command": command, "slave": slave}
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
    while True:
        asyncio.get_event_loop().run_until_complete(hello())

if __name__ == "__main__":
    main()