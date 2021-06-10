"""module to match messages and provide values for them"""
import re


class MatchFail(Exception):
    """Exception for when the message does not match"""


class _int(int):
    _lol = {69: "69 nice", 420: "420 blaze it", 666: "[censored]"}

    def __repr__(self):
        try:
            return self._lol[self]
        except KeyError:
            return int.__repr__(self)


class interpret:
    """base class for interpreted messages"""

    _value_rx = re.compile(r"[ \-+]+[\d]+")

    def __init__(self):
        raise ValueError("interpret cannot be instantiated directly")

    def _setup(self):
        self.roll = []
        self.roll_total = 0
        self.values = []
        self.min_value = None

    @property
    def total(self):
        """total is the sum of all rolls and values"""
        total = sum(self.values, self.roll_total)
        if self.min_value is not None and total < self.min_value:
            return self.min_value
        else:
            return _int(total)

    @property
    def text(self):
        """text is a printable string of the used calculation"""
        text = []
        append = text.append
        for value in self.roll:
            if value < 0:
                append(f"- {self._die}`{abs(value)}`")
            elif text:
                append(f"+ {self._die}`{value}`")
            else:
                append(f"{self._die}`{value}`")

        for value in self.values:
            if value < 0:
                append(f"- {abs(value)}")
            elif text:
                append(f"+ {value}")
            else:
                append(f"{_int(value)}")

        return " ".join(text)

    def set_roll(self, roll):
        """set the die roll

        roll: iterable of int, one for each die
        """
        self.roll = roll
        self.roll_total = sum(roll)

    def set_values(self, string):
        """interpret values

        string: str to be interpreted
        """
        self.values.clear()
        for value in self._value_rx.finditer(string):
            text = value.group(0)
            text = text.replace("+", "")
            text = text.replace(" ", "")
            text = text.replace("--", "")
            num = int(text)
            if num:
                self.values.append(num)

    def __repr__(self):
        text = f"<{self.__class__.__name__} total={self.total} "
        text += f"text={self.text}>"
        return text


class check(interpret):
    """interpreted check message"""

    _rx = re.compile(r"\b[Cc]heck([\s\-+]*\d+[\s\-+\d]*)\b")
    _die = "d10"

    def __init__(self, message):
        self._setup()
        match = self._rx.search(message)
        if not match:
            raise MatchFail("message does not match")

        value_group = match.group(1)
        self.set_values(value_group)
        self.match_end = match.end()


class damage(interpret):
    """interpreted damage message"""

    _rx = re.compile(r"\b[Dd]amage\s*([1-8])(?:d6)?([\s\-+\d]*)\b")
    _die = "d6"

    def __init__(self, message):
        self._setup()
        self.min_value = 0
        match = self._rx.search(message)
        if not match:
            raise MatchFail("message does not match")

        amount_group = match.group(1)
        self.amount = int(amount_group)
        value_group = match.group(2)
        self.set_values(value_group)
        self.match_end = match.end()
