"""Includes all the data structures such as User and Server."""
import collections

__all__ = ("User",
           "Server",
           "ServerMessage",
           "PrivmsgMessage",
           "JoinMessage",
           "PartMessage")


User = collections.namedtuple("User", ("nick", "username", "hostname"))
Server = collections.namedtuple("Server", ("hostname",))
ServerMessage = collections.namedtuple("ServerMessage",
                                       ("sender", "command", "args"))

# These are used just for the command handlers.
PrivmsgMessage = collections.namedtuple("PrivmsgMessage",
                                        ("sender", "recipient", "text"))
JoinMessage = collections.namedtuple("JoinMessage", ("sender",))
PartMessage = collections.namedtuple("PartMessage", ("sender",))
