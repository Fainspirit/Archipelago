"""Doors options"""
import typing

from Options import Option, Choice


class DoorsDummy(Choice):
    """Description"""
    displayname = "Doors Dummy"

    c0 = 0
    c1 = 1
    c2 = 2


options: typing.Dict[str, type(Option)] = {
    "doors_dummy": DoorsDummy,
}
