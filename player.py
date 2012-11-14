#!/usr/bin/env python

import waldo.lib.Waldo as Waldo
from protocol.game import Player
import config

import time

def main():
    Waldo.initialize()

    player = Waldo.connect(
        constructor = Player,

        connection_type=Waldo.CONNECTION_TYPE_TCP,
        host_name = config.host,
        port = config.port
        )

    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
