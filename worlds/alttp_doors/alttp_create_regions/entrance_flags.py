from enum import IntFlag


class EntranceType(IntFlag):
    up: 1
    down: 2
    left: 4
    right: 8

    light_world: 16
    dark_world: 32
    underworld: 64

    to_light_world: 128
    to_dark_world: 256
    to_underworld: 512
    to_dungeon: 1024

    hole: 2048

    key: 4096
    big_key: 8192
    bomb: 16384
    bonk: 32768

    portal: 65536 # TODO: Maybe warp shuffle ???