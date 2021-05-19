import logging
import os

from . import DVbot


def get_token():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    token_file = os.path.join(this_dir, ".token")
    with open(token_file) as fp:
        return fp.read()


logging.basicConfig(level=logging.INFO)
bot = DVbot()
bot.run(get_token())
