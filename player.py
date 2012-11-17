#!/usr/bin/env python

import waldo.lib.Waldo as Waldo
from protocol.lobby import Client
from protocol.game import Player
import config

import pygame
from pygame.locals import *
from pgu import gui

import time

from Queue import Queue


handlers = Queue()
def threaded(fn):
    def handler(*args, **kwargs):
        handlers.put( (fn, args, kwargs) )
    return handler

def run_handlers():
    # Safe to check empty and assume we'll get something because we're
    # the only consumer
    while not handlers.empty():
        fn, args, kwargs = handlers.get()
        fn(*args, **kwargs)


class SessionState(object):
    '''Pure state abstraction for the GUI'''
    def __init__(self, net):
        self.net = net

    def username(self):
        return self.net.get_username()

    def connected(self):
        return bool(self.username())


class LobbyGUI(object):
    def __init__(self, state, listener):
        self.state = state
        self.listener = listener

        ## GUI
        self.app = gui.Desktop()
        self.app.connect(gui.QUIT, self._handle_quit, None)

        self.layout = gui.Table(width=600, height=600)

        self.layout.tr()

        self.connected_status = gui.Image('data/delete_24.png')
        self.layout.td(self.connected_status)

        self.login_username = gui.Input()
        self.layout.td(self.login_username)

        self.login_button = gui.Button("Connect")
        self.login_button.connect(gui.CLICK, self._handle_login, None)
        self.layout.td(self.login_button)

        self.quit_button = gui.Button("Quit")
        self.quit_button.connect(gui.CLICK, self._handle_quit, None)
        self.layout.td(self.quit_button)


        self.create_game_button = gui.Button("Create New Game")
        self.create_game_button.connect(gui.CLICK, self._handle_create_game, None)

        self.games_list = gui.Table()

    def run(self):
        # Control manually so we can setup timers / process async
        # events from Waldo
        self.app.init(self.layout)
        while not self.app._quit:
            # GUI Loop
            self.app.loop()
            # Event handlers
            run_handlers()
            # Wait for next iteration
            pygame.time.wait(10)

    def set_username(self, value):
        self.login_username.value = value

    def set_connected(self, connected):
        if connected:
            self.login_button.disabled = False
            self.login_button.value = 'Change Username'
            self.set_status(True)

            # Add game listing info and control buttons
            self.layout.tr()
            self.layout.td(self.create_game_button)
            self.layout.td(self.games_list, colspan=3)

    def set_status(self, status):
        img_src = (status and 'data/check_24.png') or 'data/delete_24.png'
        img = pygame.image.load(img_src)
        if img:
            self.connected_status.value = img
            self.app.repaint()

    def set_games_list(self, games):
        self.games_list.clear()
        for g in games:
            self.games_list.tr()
            self.games_list.td(gui.Label(str(g)))
            join_button = gui.Button("Join")
            join_button.connect(gui.CLICK, self._handle_join, g)
            self.games_list.td(join_button)

    def _handle_login(self, value=None):
        username = self.login_username.value
        if not self.state.connected():
            # Disable further session requests, change text to indicate we're connecting
            self.login_button.disabled = True
            self.login_button.value = 'Connecting...'
            self.listener.on_login(username)
        else:
            self.listener.on_change_username(username)

    def _handle_create_game(self, value=None):
        self.listener.on_create_game()

    def _handle_join(self, game):
        self.listener.on_join(game)

    def _handle_quit(self, value=None):
        self.app.quit(value)


class Controller(object):
    '''Coordinates the GUI and the networking code'''

    def __init__(self):
        self.net = Waldo.connect(
            self.on_updated_open_game_list,
            self.on_matched_game,
            constructor = Client,
            host_name = config.host,
            port = config.port
            )

        self.gui = LobbyGUI(SessionState(self.net), self)

    def run(self):
        self.gui.run()

    def on_login(self, username):
        self.net.begin_session(username, self.on_began_session)

    def on_began_session(self):
        print "on_began_session"
        # Forward any possible change name back to the GUI
        self.gui.set_username(self.net.get_username())
        self.gui.set_connected(True)

    def on_change_username(self, username):
        self.net.change_username(username, self.on_change_username_response)

    def on_change_username_response(self, changed):
        print "on_change_username_response"
        # Either way, make sure we reflect the current state
        self.gui.set_username(self.net.get_username())
        self.gui.set_status(changed)

    def on_create_game(self):
        self.net.create_new_game()

    @threaded
    def on_updated_open_game_list(self, games):
        print "on_updated_open_game_list"
        self.gui.set_games_list(games)

    def on_join(self, game):
        # Try to join the game. We need to use a callback because we
        # can't get return values here. We need succeeded to be a list
        # because we need to set it in the callback
        succeeded = []
        def on_join_game_finished(suc):
            succeeded.append(suc)

        self.net.join_game(game, on_join_game_finished)
        # Block until we're sure the callback got invoked
        while len(succeeded) == 0: pass
        if succeeded[0]:
            print "Joined game", game
        else:
            print "Failed to join game", game

    @threaded
    def on_matched_game(self, guest):
        print "on_matched_game"
        print "  ", guest

def main():
    Waldo.initialize()

    controller = Controller()
    controller.run()


if __name__ == '__main__':
    main()
