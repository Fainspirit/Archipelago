"""Entrance Randomizer options"""
import typing

from Options import Option, Choice


class ERDummy(Choice):
    """Description"""
    displayname = "ER Dummy"

    option_0 = 0
    option_1 = 1
    option_2 = 2

#     ret.plando_connections = []

options: typing.Dict[str, type(Option)] = {
    "er_dummy": ERDummy,
}
