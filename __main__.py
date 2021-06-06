import logging
import os

from . import DVbot


def get_token():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    token_file = os.path.join(this_dir, ".token")
    try:
        with open(token_file) as fp:
            return fp.read()
    except OSError as exc:
        msg = f"Could not access token at {token_file}! "
        msg += "Verify the token exists and has the correct access rights, "
        msg += f"check the {os.path.join(this_dir, 'README.md')} file for "
        msg += "more information on how to run the bot."
        raise RuntimeError(msg) from exc


logging.basicConfig(level=logging.INFO)
bot = DVbot()
bot.run(get_token())
