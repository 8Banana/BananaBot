#!/usr/bin/env python3
"""The base of the project, also includes some helper functions."""
import collections
import re
import socket

__all__ = ("BananaBot",)


ACTION_FORMAT = "\x01ACTION {0}\x01"
USER_REGEXP = re.compile(
    r"^(?P<nick>.*?)!(?P<user>.*?)@(?P<host>.*?)$"
)

User = collections.namedtuple("User", ("nick", "username", "hostname"))
Server = collections.namedtuple("Server", ("hostname",))
ServerMessage = collections.namedtuple("ServerMessage",
                                       ("sender", "command", "args"))


def _parse_server_message(msg):
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
        self._dangling = ""

    def _send(self, text):
        if isinstance(text, str):
            text = text.encode("utf-8")
        if not text.endswith(b"\r\n"):
            text += b"\r\n"
        return self._socket.sendall(text)

    def send_privmsg(self, recipient, text):
        """Send a private message to a channel or an user."""
        return self._send("PRIVMSG {} :{}".format(recipient, text))

    def send_action(self, recipient, act):
        """Send an action to a channel or an user."""
        return self.send_privmsg(recipient, ACTION_FORMAT.format(act))

    def _recv_message(self):
        if not self._linebuffer:
            buf = self._socket.recv(4096)
            if self._dangling:
                buf = self._dangling + buf
                self._dangling = ""
            lines = buf.decode("utf-8").split("\r\n")
            self._dangling += lines.pop()
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
        while True:
            msg = self._recv_message()
            if msg.command == "PING":
                self._send("PONG {}".format(" ".join(msg.args)))
