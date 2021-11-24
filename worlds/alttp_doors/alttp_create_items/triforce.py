from worlds.alttp_doors.legacy.item_data import ItemFactory

def handle_triforce_placement(autoworld):
    world = autoworld.world
    player = autoworld.player

    if autoworld.game_settings["goal"].requires_ganon:
        world.push_item(world.get_location('Ganon', player), autoworld.create_item('Triforce'), False)
    else:
        world.push_item(world.get_location('Ganon', player), autoworld.create_item('Nothing'), False)