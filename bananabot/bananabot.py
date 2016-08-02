#!/usr/bin/env python3
"""The base of the project, also includes some helper functions."""
import collections
import socket

from . import commands
from .parsing import (parse_server_message,
                      parse_privmsg, parse_join, parse_part, parse_command)

__all__ = ("BananaBot",)


ACTION_FORMAT = "\x01ACTION {0}\x01"


class BananaBot:
    """
    The base for the project, an IRC bot.

    However, this should be handled via the `__main__.py` file.
    """

    def __init__(self, config):
        """
        Initialize a BananaBot instance.

        Args:
            config(dict): The configuration file for the bot.
        """
        self.config = config
        self._socket = socket.socket()
        self._linebuffer = collections.deque()
        self._dangling = b""

    def _send(self, msg):
        try:
            msg = msg.encode("utf-8")
        except AttributeError:
            pass
        msg += b"\r\n"
        self._socket.sendall(msg)

    def send_privmsg(self, recipient, text):
        """Send a private message to a channel or an user."""
        return self._send("PRIVMSG {} :{}".format(recipient, text))

    def send_action(self, recipient, act):
        """Send an action to a channel or an user."""
        return self.send_privmsg(recipient, ACTION_FORMAT.format(act))

    def join_channel(self, channel):
        """Join an IRC channel."""
        self._send("JOIN {}".format(channel))

    def _recv_message(self):
        while not self._linebuffer:
            buf = self._socket.recv(4096)
            if self._dangling:
                buf = self._dangling + buf
                self._dangling = b""
            lines = buf.decode("utf-8").split("\r\n")
            # We re-encode the line here just so we can keep it in bytes,
            # seeing as we'd have to encode/decode it at some point anyways.
            self._dangling += lines.pop().encode("utf-8")
            self._linebuffer.extend(lines)
        return parse_server_message(self._linebuffer.popleft())

    def _connect(self):
        self._socket.connect((self.config["host"], self.config["port"]))

    def _identify(self):
        self._send("NICK {}".format(self.config["nickname"]))
        self._send("USER {0} * * {0}".format(self.config["nickname"]))

    def mainloop(self):
        """Run the bot until the heat death of the universe."""
        self._connect()
        self._identify()
        for channel in self.config["channels"]:
            self.join_channel(channel)
        while True:
            msg = self._recv_message()
            if msg.command == "PING":
                self._send("PONG {}".format(" ".join(msg.args)))
            elif msg.command == "PRIVMSG":
                privmsg = parse_privmsg(msg)
                for handler in commands.handlers["privmsg"]:
                    handler(self, privmsg)
                command = parse_command(privmsg)
                if command is not None:
                    try:
                        handler = commands.handlers["command"][command.command]
                    except KeyError:
                        pass
                    else:
                        handler(self, command)
            elif msg.command == "JOIN":
                join = parse_join(msg)
                for handler in commands.handlers["join"]:
                    handler(self, join)
            elif msg.command == "PART":
                part = parse_part(msg)
                for handler in commands.handlers["part"]:
                    handler(self, part)
