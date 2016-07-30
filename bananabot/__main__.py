#!/usr/bin/env python3
# flake8: noqa
import argparse

import bananabot


def main():
    argp = argparse.ArgumentParser("bananabot")
    argp.add_argument("configfile", nargs="?", default="config.yaml",
                      help="The relative path to your config file.")
    argv = argp.parse_args()
    with open(argv.configfile) as config_fobj:
        bananabot.BananaBot(yaml.load(config_fobj)).mainloop()

if __name__ == "__main__":
    main()
