import asyncio
import logging

import discord

from . import interpret
from . import roll
from . import table

_color = discord.Color
DAMAGE_CURVE = 3
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


def _index_of_dv(amount):
    for index, (name, description, value) in enumerate(table.DV):
        if amount <= value:
            return index
    else:
        return index + 1  # this is len(table.DV)


class _damage_color(_color):
    _steepness = 1 / DAMAGE_CURVE  # higher values are more linear
    _max_amount = 50  # expected highest value
    _max_grade = 0xFF  # one byte
    # look for correction value that matches steepness
    _correction = _max_grade / _max_amount ** _steepness

    def __init__(self, amount):
        amount = max(amount, 0)
        grade = round(amount ** self._steepness * self._correction)
        color = min(grade << 16, 0xFF0000)  # shift to red
        super().__init__(color + 0x3333)  # a little gray


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
        check.set_roll([roll.MAX_D10])
        max_result = check.total
        result = roll.check()
        check.set_roll(result)
        index = _index_of_dv(check.total)
        status = ""
        if index:
            name, *_ = table.DV[index - 1]
            status = f" {name}!"

        total = check.total
        self.log(f"rolled check {total}/{max_result} {check.text}{status}")
        embed = discord.Embed(title=total)
        embed.description = check.text
        embed.color = DV_COLORS[index]
        return embed

    def make_damage(self, damage):
        damage.set_roll([roll.MAX_D6 * damage.amount])
        max_result = damage.total
        result = roll.damage(damage.amount)
        is_crit = roll.sorted_is_critical(result)
        damage.set_roll(result)
        crit = " critical injury!" if is_crit else ""
        total = damage.total
        color = _damage_color(total)
        self.log(
            f"rolled damage {total}/{max_result} {damage.text}{crit} {color}"
        )
        embed = discord.Embed(title=total)
        embed.description = damage.text + crit
        embed.color = color
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

        cors = [
            message.remove_reaction(emoji, self.user)
            for emoji in self.reactions
        ]
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
