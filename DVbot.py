import asyncio
import logging

import discord

from . import reply

DIE_EMOJI = "🎲"
TRASH_EMOJI = "🚮"
PATIENCE_EMOJI = "🕰️"


class DVbot(discord.Client):
    """DVbot

    a discord bot to roll d10s with
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.my_logger = logging.getLogger(self.__class__.__name__)
        self.last_messages = {}
        self.reactions = [DIE_EMOJI, TRASH_EMOJI]

    def log(self, msg):
        self.my_logger.info(msg)

    async def on_ready(self):
        self.log(f"{self.user} has logged in to {len(self.guilds)} guilds")

    async def on_message(self, message):
        user = message.author
        if user == self.user:
            return

        try:
            got = reply.reply(self.log, message)
        except reply.MatchFail:
            return

        try:
            last_message = self.last_messages[user]
        except KeyError:
            last_message = None
        else:
            if last_message.sent is None:
                # we are still processing this user's last message
                await message.add_reaction(PATIENCE_EMOJI)
                return

        # it's possible for a race condition to occur here where the previous
        # reacts on a message are not removed
        # this is rare however and not worth proofing for, considering the
        # nonfunctional reacts are only visual anyway
        self.last_messages[user] = got
        got.roll()
        if last_message is None:
            await self._send_reply(got)
        else:
            await asyncio.gather(
                self._send_reply(got),
                self._remove_last_emojis(last_message),
            )

    async def _send_reply(self, reply_):
        channel = reply_.source.channel
        message = await channel.send(embed=reply_.embed)
        cors = [message.add_reaction(emoji) for emoji in self.reactions]
        await asyncio.gather(*cors)
        reply_.sent = message

    async def _remove_last_emojis(self, message):
        cors = [
            message.sent.remove_reaction(emoji, self.user)
            for emoji in self.reactions
        ]
        try:
            await asyncio.gather(*cors)
        except discord.NotFound:
            pass  # do not remove from last_messages, message will be replaced

    async def _del_last_message(self, message):
        del self.last_messages[message.user]
        try:
            await message.sent.delete()
        except discord.NotFound:
            pass

    async def on_reaction_add(self, reaction, user):
        if user == self.user or reaction.message.author != self.user:
            return

        try:
            message = self.last_messages[user]
        except KeyError:
            return

        if message.sent != reaction.message or message.user != user:
            return

        if reaction.emoji == DIE_EMOJI:
            try:
                message.reinterpret(message.source.content)
            except reply.MatchFail:
                self._del_last_message(message)
            else:
                message.roll()
                await message.sent.edit(embed=message.embed)
        elif reaction.emoji == TRASH_EMOJI:
            await self._del_last_message(message)
        elif reaction.emoji == PATIENCE_EMOJI:
            await message.sent.edit(content=":upside_down:")
