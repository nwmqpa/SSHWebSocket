"""SSH WebSocketServer."""
import sys
import random
import json
import subprocess
import sys
import os
from twisted.web.static import File
from twisted.python import log
from twisted.web.server import Site
from twisted.internet import reactor
from autobahn.twisted import websocket


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
                self.factory.register_slave(self, returned["name"], returned["pswd"])
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
        for i, v in self.clients.items():
            if v["name"] == infos["slave"]:
                if infos["pswd"] == v["pswd"]:
                    self.links.append({"master": client, "slave": infos["slave"]})
                    v["object"].sendMessage(infos["command"].encode())
                else:
                    client.sendMessage(json.dumps({"stderr": "Bad password !", "stdout": ""}).encode())

    def register_slave(self, client, slave_uuid, slave_pswd):
        """Register a slave to the list of slaves."""
        self.clients[client.peer]["name"] = slave_uuid
        self.clients[client.peer]["pswd"] = slave_pswd

    def list_clients(self, client):
        """List all clients registered."""
        slaves = []
        for i in self.clients:
            slaves.append(self.clients[i].copy())
            del slaves[-1]["object"]
        client.sendMessage(json.dumps(slaves).encode())


def main():
    log.startLogging(sys.stdout)
    factory = WebSSHFactory("ws://0.0.0.0:8080")
    factory.protocol = SomeServerProtocol
    reactor.listenTCP(8080, factory)
    reactor.run()


if __name__ == "__main__":
    main()