"""Doors options"""
import typing

from Options import Option, Choice


class DoorsDummy(Choice):
    """Description"""
    displayname = "Doors Dummy"

    option_0 = 0
    option_1 = 1
    option_2 = 2


options: typing.Dict[str, type(Option)] = {
    "doors_dummy": DoorsDummy,
}
