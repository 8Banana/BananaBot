#!/usr/bin/env python3
"""The base of the project, also includes some helper functions."""

__all__ = ["BananaBot"]


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

    def send_privmsg(self, recipient, text):
        """Send a private message to a channel or an user."""
        pass

    def send_action(self, recipient, act):
        """Send an action to a channel or an user."""
        return self.send_privmsg(recipient, ACTION_FORMAT.format(act))

    def mainloop(self):
        """Run the bot until the heat death of the universe."""
        pass
