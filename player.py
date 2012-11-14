#!/usr/bin/env python

import waldo.lib.Waldo as Waldo
from protocol.lobby import Client
from protocol.game import Player
import config

import pygame
from pygame.locals import *
from pgu import gui

import time

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

        self.layout = gui.Table(width=600, height=120)

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

    def run(self):
        self.app.run(self.layout)

    def set_username(self, value):
        self.login_username.value = value

    def set_connected(self, connected):
        if connected:
            self.login_button.disabled = False
            self.login_button.value = 'Change Username'
            self.set_status(True)

    def set_status(self, status, timeout=None):
        img_src = (status and 'data/check_24.png') or 'data/delete_24.png'
        print 'loading', img_src, status
        img = pygame.image.load(img_src)
        print img
        if img:
            self.connected_status.value = img
            self.app.repaint()

        if timeout is not None:
            pass

    def _handle_login(self, value=None):
        username = self.login_username.value
        if not self.state.connected():
            # Disable further session requests, change text to indicate we're connecting
            self.login_button.disabled = True
            self.login_button.value = 'Connecting...'
            self.listener.on_login(username)
        else:
            self.listener.on_change_username(username)

    def _handle_quit(self, value=None):
        self.app.quit(value)

class Controller(object):
    '''Coordinates the GUI and the networking code'''

    def __init__(self):
        self.net = Waldo.connect(
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
        # Forward any possible change name back to the GUI
        self.gui.set_username(self.net.get_username())
        self.gui.set_connected(True)

    def on_change_username(self, username):
        self.net.change_username(username, self.on_change_username_response)

    def on_change_username_response(self, changed):
        # Either way, make sure we reflect the current state
        self.gui.set_username(self.net.get_username())
        print changed
        self.gui.set_status(changed)

def main():
    Waldo.initialize()

    controller = Controller()
    controller.run()


if __name__ == '__main__':
    main()
