#!/usr/bin/env python

import waldo.lib.Waldo as Waldo
from protocol.game import Server
import config

def on_connection(client):
    print "Received client connection"

def main():
    Waldo.initialize()
    Waldo.accept(
        constructor = Server,

        connection_type=Waldo.CONNECTION_TYPE_TCP,
        host_name = config.host,
        port = config.port,

        connected_callback=on_connection
        )

if __name__ == '__main__':
    main()
