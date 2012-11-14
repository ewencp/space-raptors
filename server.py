#!/usr/bin/env python

import waldo.lib.Waldo as Waldo
from protocol.lobby import Lobby
from protocol.game import Server
import config

class LobbyServer:

    def __init__(self):
        self._users = Waldo.ExternalList([])
        Waldo.accept(
            self._users,
            constructor = Lobby,
            host_name = config.host,
            port = config.port,
            connected_callback=self.on_connection
            )

    def on_connection(self, client):
        print "Received client connection"


def main():
    Waldo.initialize()
    lobby = LobbyServer()

if __name__ == '__main__':
    main()
