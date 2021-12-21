from worlds import AutoWorld


def handle_remove_starting_inventory_from_pool(autoworld: AutoWorld):
    start_inv = autoworld.game_settings["start_inventory"].value
    item_pool = autoworld.item_pool
    for k in start_inv:
        if k in item_pool:  # If it was going to be placed
            item_pool[k] = max(0, item_pool[k] - start_inv[k]) # Set it to amount given, or 0 if more than in pool
