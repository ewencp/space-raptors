#!/usr/bin/env python

import waldo.lib.Waldo as Waldo
from protocol.lobby import Lobby
from protocol.game import Server
import config

class LobbyServer:

    def __init__(self):
        self._connections = []

        self._users = Waldo.ExternalList([])
        self._matching_users = Waldo.ExternalList([])
        self._open_games = Waldo.ExternalList([])
        self._active_games = Waldo.ExternalList([])
        Waldo.accept(
            self._users,
            self._matching_users,
            self._open_games,
            self._active_games,
            self.on_open_game_added,
            self.on_matched_game,
            constructor = Lobby,
            host_name = config.host,
            port = config.port,
            connected_callback=self.on_connection
            )

    def on_connection(self, conn):
        print "Received client connection"
        self._connections.append(conn)

    def on_open_game_added(self):
        '''When a new game is opened (advertised) by a user, we need
        to notify other connections about the new game in case they
        are still looking for games. The Waldo code will filter out
        ones that don't need to see the change (they are already
        matched and in a game)'''
        for conn in self._connections:
            conn.push_game_list()

    def on_matched_game(self, owner, guest):
        print "Matched game between %s and %s" % (owner, guest)
        print "Pushing updated game lists for all clients"
        for conn in self._connections:
            conn.push_game_list()
            # Notify the owner that they're in a game now.
            # It sucks that we have to do this for everyone, but we'll
            # only send anything to the owner (everyone else gets
            # filtered before hitting a sequence). We can't find the
            # right person since only have connection objects in
            # Python-land.
            conn.notify_owner_of_guest(owner, guest)

def main():
    Waldo.initialize()
    lobby = LobbyServer()

if __name__ == '__main__':
    main()
