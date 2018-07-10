"""SSH WebSocketServer."""
import sys
import random
import json
import subprocess
import sys
import os
from urllib.request import urlopen, urlcleanup
from twisted.web.static import File
from twisted.python import log
from twisted.web.server import Site
from twisted.internet import reactor
from autobahn.twisted import websocket

"""Current version of the program."""
VERSION = "0.0.3"

"""Startup CWD of the program."""
STARTUP_CWD = os.getcwd()

"""Online file containing the newest version number."""
VERSION_FILE = (
    "https://raw.githubusercontent.com/nwmqpa/SSHWebSocket/master/dns_server/version"
)

"""Online file containing the updated source code."""
SOURCE_FILE = (
    "https://raw.githubusercontent.com/nwmqpa/SSHWebSocket/master/dns_server/__main__.py"
)


class SomeServerProtocol(websocket.WebSocketServerProtocol):
    """Protocol defining where are the messages sended."""

    def onOpen(self):
        """
        Load on opening client socket.

        Connection from client is opened. Fires after opening
        websockets handshake has been completed and we can send
        and receive messages.

        Register client in factory, so that it is able to track it.
        """
        self.factory.register(self)

    def connectionLost(self, reason):
        """
        Load on lost connection with client.

        Client lost connection, either disconnected or some error.
        Remove client from list of tracked connections.
        """
        self.factory.unregister(self)

    def onMessage(self, payload, isBinary):
        """
        Load on receiving a message from client.

        Message sent from clien/ssh_servert, communicate this message to
        the right function.
        """
        try:
            returned = json.loads(payload.decode())
        except json.decoder.JSONDecodeError:
            if payload.decode() == "list":
                self.factory.list_clients(self)
            else:
                print("Unknown message.")
        else:
            if "type" in returned.keys():
                self.factory.register_slave(self, returned["name"])
            if "stdout" in returned.keys():
                self.factory.sendReturn(self, returned)
            if "command" in returned.keys():
                self.factory.sendCommand(self, returned)


class WebSSHFactory(websocket.WebSocketServerFactory):
    """Class defining the behaviour of the application."""

    def __init__(self, *args, **kwargs):
        """Initialize the object."""
        super(WebSSHFactory, self).__init__(*args, **kwargs)
        self.clients = {}
        self.slaves = []
        self.links = []

    def register(self, client):
        """Add client to list of managed connections."""
        self.clients[client.peer] = {"object": client, "name": None}

    def unregister(self, client):
        """Remove client from list of managed connections."""
        self.clients.pop(client.peer)

    def communicate(self, client, payload, isBinary):
        """Broker message from client to its partner."""
        c = self.clients[client.peer]

    def sendReturn(self, client, infos):
        """Send the return values of the previous command to the sender."""
        slave = None
        for i, v in self.clients.items():
            if v["object"] == client:
                slave = v["name"]
                break
        for v in self.links:
            if v["slave"] == slave:
                v["master"].sendMessage(json.dumps(infos).encode())
                self.links.pop(self.links.index(v))
                break

    def sendCommand(self, client, infos):
        """Send a command to the registered slave."""
        self.links.append({"master": client, "slave": infos["slave"]})
        for i, v in self.clients.items():
            if v["name"] == infos["slave"]:
                v["object"].sendMessage(infos["command"].encode())

    def register_slave(self, client, slave_uuid):
        """Register a slave to the list of slaves."""
        self.clients[client.peer]["name"] = slave_uuid

    def list_clients(self, client):
        """List all clients registered."""
        slaves = []
        for i in self.clients:
            slaves.append(self.clients[i].copy())
            del slaves[-1]["object"]
        client.sendMessage(json.dumps(slaves).encode())


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
    log.startLogging(sys.stdout)
    factory = WebSSHFactory(u"ws://0.0.0.0:8080")
    factory.protocol = SomeServerProtocol
    reactor.listenTCP(8080, factory)
    reactor.run()
