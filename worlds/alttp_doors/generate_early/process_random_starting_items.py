import random

from BaseClasses import MultiWorld
from worlds.alttp_doors.legacy.item_pool import get_pool_core


def process_random_starting_items(amount: int, world: MultiWorld, player: int):
    # Invalid starting item
    pool = list(filter(lambda name: name != "Triforce Piece", get_pool_core(world, player)[0]))

    chosen_items = random.sample(pool, min(
        pool.__len__(),
        amount))
    new_items = {}

    existing = world.start_inventory[player].value
    for name in chosen_items:
        if name in new_items:
            new_items[name] += 1
        else:
            new_items[name] = 1

    existing |= new_items
    world.start_inventory[player].value = existing



