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

    # Item pool has already been established
    src = autoworld.item_pool

    # Make list of the items for random pick
    pool = []
    for k in src:
        if k not in invalid_items:
            for i in range(src[k]):
                pool.append(k)

    chosen_items = random.sample(pool, min(
        pool.__len__(),
        amount))

    existing = autoworld.game_settings["start_inventory"].value

    # Combine Start Inventory
    for item in chosen_items:
        if item in existing:
            existing[item] += 1
        else:
            existing[item] = 1

    autoworld.game_settings["start_inventory"].value = existing
    pass


