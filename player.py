#!/usr/bin/env python

import waldo.lib.Waldo as Waldo
from protocol.lobby import Client
from protocol.game import Player
import config

import pygame
from pygame.locals import *
from pgu import gui

import time

class LobbyGUI(object):

    def __init__(self, listener):
        self.listener = listener

        ## GUI
        self.app = gui.Desktop()
        self.app.connect(gui.QUIT, self._handle_quit, None)

        self.layout = gui.Table(width=200, height=120)

        self.layout.tr()

        self.login_username = gui.Input()
        self.layout.td(self.login_username)

        self.login_button = gui.Button("Connect")
        self.login_button.connect(gui.CLICK, self._handle_login, None)
        self.layout.td(self.login_button)

        self.quit_button = gui.Button("Quit")
        self.quit_button.connect(gui.CLICK, self._handle_quit, None)
        self.layout.td(self.quit_button)

    def run(self):
        self.app.run(self.layout)

    def set_username(self, value):
        self.login_username.value = value

    def set_connected(self, connected):
        if connected:
            self.login_button.value = 'Connected'

    def _handle_login(self, value=None):
        username = self.login_username.value
        # Disable further session requests, change text to indicate we're connecting
        self.login_button.disabled = True
        self.login_button.value = 'Connecting...'
        self.listener.on_login(username)

    def _handle_quit(self, value=None):
        self.app.quit(value)

class Controller(object):
    '''Coordinates the GUI and the networking code'''

    def __init__(self):
        self.net = Waldo.connect(
            self.on_began_session,

            constructor = Client,
            host_name = config.host,
            port = config.port
            )

        self.gui = LobbyGUI(self)

    def run(self):
        self.gui.run()

    def on_login(self, username):
        self.net.begin_session(username)

    def on_began_session(self):
        # Forward any possible change name back to the GUI
        self.gui.set_username(self.net.get_username())
        self.gui.set_connected(True)

def main():
    Waldo.initialize()

    controller = Controller()
    controller.run()


if __name__ == '__main__':
    main()
