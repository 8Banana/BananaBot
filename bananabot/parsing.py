"""Includes all the parsing for server messages."""
import re

from .datastructures import (User, Server, ServerMessage,
                             PrivmsgMessage, JoinMessage, PartMessage)

__all__ = ("parse_server_message", "parse_privmsg", "parse_join", "parse_part")

USER_REGEXP = re.compile(
    r"^(?P<nick>.*?)!(?P<user>.*?)@(?P<host>.*?)$"
)


def parse_server_message(msg):
    """Parse a server message line and turn it into a ServerMessage tuple."""
    # Watch out, MSG is bad for you!
    # ASSUMPTION: The message has the sender information.
    sender_info, msg = msg[1:].split(" ", 1)
    args = msg.split(" ")
    command = args.pop(0)
    for n, i in enumerate(args[:]):
        if i.startswith(":"):
            temp = args[n:]
            args = args[:n]
            args.append(" ".join(temp)[1:])
            break
    if "!" in sender_info:
        match = USER_REGEXP.match(sender_info)
        assert match is not None
        user = User(match.group("nick"),
                    match.group("user"),
                    match.group("host"))
        return ServerMessage(user, command, args)
    else:
        server = Server(sender_info,)
        return ServerMessage(server, command, args)


def parse_privmsg(msg):
    """Parse a ServerMessage representing a PRIVMSG."""
    if isinstance(msg, str):
        msg = parse_server_message(msg)
    return PrivmsgMessage(msg.sender, msg.args[0], msg.args[1])


def parse_join(msg):
    """Parse a ServerMessage representing a JOIN."""
    if isinstance(msg, str):
        msg = parse_server_message(msg)
    return JoinMessage(msg.sender)


def parse_part(msg):
    """Parse a ServerMessage representing a PART."""
    if isinstance(msg, str):
        msg = parse_server_message(msg)
    return PartMessage(msg.sender)