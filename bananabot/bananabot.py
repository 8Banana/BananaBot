#!/usr/bin/env python3
"""The base of the project, also includes some helper functions."""
import collections
import re
import socket

from . import commands

__all__ = ("BananaBot",)


ACTION_FORMAT = "\x01ACTION {0}\x01"
USER_REGEXP = re.compile(
    r"^(?P<nick>.*?)!(?P<user>.*?)@(?P<host>.*?)$"
)

User = collections.namedtuple("User", ("nick", "username", "hostname"))
Server = collections.namedtuple("Server", ("hostname",))
ServerMessage = collections.namedtuple("ServerMessage",
                                       ("sender", "command", "args"))

# These are used just for the command handlers.
PrivmsgMessage = collections.namedtuple("PrivmsgMessage",
                                        ("sender", "recipient", "text"))
JoinMessage = collections.namedtuple("JoinMessage", ("sender",))
PartMessage = collections.namedtuple("PartMessage", ("sender",))


def _parse_server_message(msg):
    """Parse a server message line and turn it into a ServerMessage tuple."""
    # Watch out, MSG is bad for you!
    # ASSUMPTION: The message has the sender information.
    sender_info, msg = msg[1:].split(" ", 1)
    if "!" in sender_info:
        match = USER_REGEXP.match(sender_info)
        assert match is not None
        sender = User(match.group("nick"),
                      match.group("user"),
                      match.group("host"))
    else:
        sender = Server(sender_info,)
    args = msg.split(" ")
    command = args.pop(0)
    for n, i in enumerate(args[:]):
        if i.startswith(":"):
            temp = args[n:]
            args = args[:n]
            args.append(" ".join(temp)[1:])
            break
    return ServerMessage(sender, command, args)


def _parse_privmsg(msg):
    if isinstance(msg, str):
        msg = _parse_server_message(msg)
    return PrivmsgMessage(msg.sender, msg.args[0], msg.args[1])


def _parse_join(msg):
    if isinstance(msg, str):
        msg = _parse_server_message(msg)
    return JoinMessage(msg.sender)


def _parse_part(msg):
    if isinstance(msg, str):
        msg = _parse_server_message(msg)
    return PartMessage(msg.sender)


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
        if not self._linebuffer:
            buf = self._socket.recv(4096)
            if self._dangling:
                buf = self._dangling + buf
                self._dangling = b""
            lines = buf.decode("utf-8").split("\r\n")
            # We re-encode the line here just so we can keep it in bytes,
            # seeing as we'd have to encode/decode it at some point anyways.
            self._dangling += lines.pop().encode("utf-8")
            self._linebuffer.extend(lines)
        return _parse_server_message(self._linebuffer.popleft())

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
                privmsg = _parse_privmsg(msg)
                for handler in commands.handlers["privmsg"]:
                    handler(privmsg)
            elif msg.command == "JOIN":
                join = _parse_join(msg)
                for handler in commands.handlers["join"]:
                    handler(join)
            elif msg.command == "PART":
                part = _parse_part(msg)
                for handler in commands.handlers["part"]:
                    handler(part)
