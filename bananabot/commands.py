"""This module is sort of a config file for all the command handlers."""

__all__ = ("handlers",)

handlers = {
    "join": [],
    "part": [],
    "privmsg": [],
    "command": {"!echo": lambda b, c: b.send_privmsg(c.recipient, c.arg_text)},
}
