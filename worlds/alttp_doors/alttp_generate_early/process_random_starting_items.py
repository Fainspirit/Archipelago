import random

from BaseClasses import MultiWorld
from worlds.alttp_doors.legacy.item_pool import get_pool_core, generate_itempool

# TODO - make this somehow be able to work off an existing pool (with all copies of everything). Maybe move it later and set the precollected items manually
def handle_random_starting_items(autoworld):
    amount = autoworld.game_settings["random_starting_item_amount"]
    player = autoworld.player
    world = autoworld.world
    
    # Invalid starting items
    invalid_items = ["Triforce Piece", "Red Clock", "Blue Clock", "Green Clock",
                     "Small Heart", "Power Star", "Faerie", "Bee Trap", "Nothing",
                     "Blue Potion", "Red Potion", "Green Potion", "Bee", "Apple",
                     "Good Bee", "Rupoor", "Single RNG", "Multi RNG", "Triforce", "Magic Jar"] # What is magic jar?
    #src = get_pool_core(world, player)[0]
    # This is too soon
    #src = world.worlds[player].itempool
    from worlds.alttp_doors import item_name_groups
    src = item_name_groups['Everything']

    pool = list(filter(lambda name: name not in invalid_items, src))

    chosen_items = random.sample(pool, min(
        pool.__len__(),
        amount))
    new_items = {}

    existing = autoworld.game_settings["start_inventory"].value
    for name in chosen_items:
        if name in new_items:
            new_items[name] += 1
        else:
            new_items[name] = 1

    existing |= new_items
    autoworld.game_settings["start_inventory"].value = existing
    pass


