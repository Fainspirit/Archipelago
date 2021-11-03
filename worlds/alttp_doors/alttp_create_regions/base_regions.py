def handle_base_regions(autoworld):
    world_state = autoworld.game_settings["world_state"]
    # TODO: match case python 3.10

    if world_state == "open":
        handle_open_regions(autoworld)
    elif world_state == "standard":
        handle_standard_regions(autoworld)
    elif world_state == "inverted":
        handle_inverted_regions(autoworld)

def handle_open_regions(autoworld):
    from ..memory_data.region_data import create_regions
    create_regions(autoworld.world, autoworld.player)

def handle_standard_regions(autoworld):
    pass

def handle_inverted_regions(autoworld):
    pass