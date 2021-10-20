"""Entrance Randomizer options"""
import typing

from Options import Option, Choice


class ERDummy(Choice):
    """Description"""
    displayname = "ER Dummy"

    c0 = 0
    c1 = 1
    c2 = 2


options: typing.Dict[str, type(Option)] = {
    "er_dummy": ERDummy,
}
