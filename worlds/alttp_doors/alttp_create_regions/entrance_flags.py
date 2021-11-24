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

    low_layer: 131072
    high_layer: 262144

    straight_stairs: 524288
    spiral_stairs: 1048576

# TODO - specify somewhere mask types to know which edges can be swapped with which
# Probably put this on a parameter for the rando so that different swap modes can access it

# TODO - something for syncing two way entrance swap