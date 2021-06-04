import asyncio
import logging
import re

import discord

from . import interpret
from . import roll
from . import table

_color = discord.Color
DIE_EMOJI = "🎲"
TRASH_EMOJI = "🚮"
DV_COLORS = (
    _color.red(),
    _color.orange(),
    _color.gold(),
    _color.green(),
    _color.teal(),
    _color.blue(),
    _color.purple(),
    _color.magenta(),
)
DAMAGE_COLOR = _color.dark_gray()


def _index_of_dv(amount):
    for index, (name, description, value) in enumerate(table.DV):
        if amount <= value:
            return index
    else:
        return index + 1  # this is len(table.DV)


class DVbot(discord.Client):
    """DVbot

    a discord bot to roll d10s with
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.my_logger = logging.getLogger(self.__class__.__name__)
        self.last_message = None
        self.reactions = [DIE_EMOJI, TRASH_EMOJI]

    def log(self, msg):
        self.my_logger.info(msg)

    def make_check(self, check):
        result = roll.check()
        check.set_roll(result)
        index = _index_of_dv(check.total)
        status = ""
        if index:
            name, *_ = table.DV[index - 1]
            status = f" {name}!"

        self.log(f"rolled check {check.text}{status}")
        embed = discord.Embed(title=check.total)
        embed.description = check.text
        embed.color = DV_COLORS[index]
        return embed

    def make_damage(self, damage):
        result = roll.damage(damage.amount)
        is_crit = roll.sorted_is_critical(result)
        damage.set_roll(result)
        crit = " critical injury!" if is_crit else ""
        self.log(f"rolled damage {damage.text}{crit}")
        embed = discord.Embed(title=damage.total)
        embed.description = damage.text + crit
        embed.color = DAMAGE_COLOR
        return embed

    async def on_ready(self):
        self.log(f"{self.user} has logged in")

    async def on_message(self, message):
        if message.author == self.user:
            return

        content = message.content
        try:
            check = interpret.check(content)
        except interpret.MatchFail:
            pass
        else:
            embed = self.make_check(check)
            self.last_source_id = message.id
            self.last_message, _ = await asyncio.gather(
                self._send_embed(message.channel, embed),
                self._remove_last_emojis(self.last_message),
            )
            return

        try:
            damage = interpret.damage(content)
        except interpret.MatchFail:
            pass
        else:
            embed = self.make_damage(damage)
            await message.channel.send(embed=embed)
            return

    async def _send_embed(self, channel, embed):
        message = await channel.send(embed=embed)
        cors = [message.add_reaction(emoji) for emoji in self.reactions]
        await asyncio.gather(*cors)
        return message

    async def _remove_last_emojis(self, message):
        if message is None:
            return

        cors = [message.remove_reaction(emoji, self.user) for emoji in self.reactions]
        await asyncio.gather(*cors)

    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        if user == self.user or message != self.last_message:
            return

        if reaction.emoji == DIE_EMOJI:
            channel = self.last_message.channel
            try:
                source = await channel.fetch_message(self.last_source_id)
                check = interpret.check(source.content)
            except (discord.NotFound, interpret.MatchFail):
                await message.delete()
            else:
                embed = self.make_check(check)
                await message.edit(embed=embed)
        elif reaction.emoji == TRASH_EMOJI:
            await message.delete()
