import discord

from . import interpret
from . import roll
from . import table
from .interpret import MatchFail

_color = discord.Color
DAMAGE_CURVE = 3
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
            return index, name
    else:
        return index + 1, ""  # this is len(table.DV)


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


_interprets = {}


def _add_interpret(interpret_):
    def wrap(fun):
        _interprets[interpret_] = fun
        return fun

    return wrap


class reply:
    """a reply to a message

    log:
        function for logging
    message:
        a sent message to reply to as str
    """

    def __init__(self, log, source):
        self.log = log
        self.sent = None
        self.source = source
        self.user = source.author
        self.reinterpret(source.content)

    def reinterpret(self, message):
        """refresh the message

        message:
            a sent message to reply to as str
        """
        if not message:
            raise ValueError("message is empty")

        self.set_color = False
        self.embed = discord.Embed()
        self.fun_to_end = {}
        for option, fun in _interprets.items():
            content = message
            end = 0
            while content:
                try:
                    got = option(content)
                except MatchFail:
                    break

                end += got.match_end
                content = message[end:]
                if got.multiple != 0:
                    self.fun_to_end[end] = fun, got

        if not self.fun_to_end:
            raise MatchFail("reply does not match")

    def roll(self):
        """roll the previously interpreted message"""
        for end in sorted(self.fun_to_end):
            fun, got = self.fun_to_end[end]
            for _ in range(got.multiple):
                fun(self, got)
                self.set_color = True

    @_add_interpret(interpret.check)
    def make_check(self, check):
        check.set_roll([roll.MAX_D10])
        max_result = check.total
        result = roll.check()
        check.set_roll(result)
        total = check.total
        index, name = _index_of_dv(total)
        status = ""
        if name:
            status = f" {name}!"

        title = f"check: {check.total}"
        self.log(f"rolled {title}/{max_result} {check.text}{status}")
        self.embed.add_field(name=title, value=check.text)
        if not self.set_color:  # set color only for first item
            self.embed.color = DV_COLORS[index]

    @_add_interpret(interpret.damage)
    def make_damage(self, damage):
        damage.set_roll([roll.MAX_D6 * damage.amount])
        max_result = damage.total
        result = roll.damage(damage.amount)
        is_crit = roll.sorted_is_critical(result)
        damage.set_roll(result)
        text = damage.text
        if is_crit:
            text += " critical injury!"

        total = damage.total
        title = f"damage: {total}"
        color = _damage_color(total)
        self.log(f"rolled {title}/{max_result} {text} {color}")
        self.embed.add_field(name=title, value=text)
        if not self.set_color:  # set color only for first item
            self.embed.color = color
