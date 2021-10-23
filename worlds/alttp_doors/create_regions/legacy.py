import random

from BaseClasses import Region, RegionType, Entrance
from worlds.alttp_doors.legacy.entrance_randomizer_shuffle import link_entrances, link_inverted_entrances, \
    plando_connect
from worlds.alttp_doors.memory_data.location_data import location_table


def create_regions(self):
    from worlds.alttp_doors.legacy.dungeons import create_dungeons
    from worlds.alttp_doors.legacy.inverted_regions import create_inverted_regions
    from worlds.alttp_doors.legacy.shop import create_shops
    from worlds.alttp_doors.memory_data.region_data import create_regions

    player = self.player
    world = self.world


    if world.open_pyramid[player] == 'goal':
        world.open_pyramid[player] = world.goal[player] in {'crystals', 'ganontriforcehunt',
                                                            'localganontriforcehunt', 'ganonpedestal'}
    elif world.open_pyramid[player] == 'auto':
        world.open_pyramid[player] = world.goal[player] in {'crystals', 'ganontriforcehunt',
                                                            'localganontriforcehunt', 'ganonpedestal'} and \
                                     (world.shuffle[player] in {'vanilla', 'dungeonssimple', 'dungeonsfull',
                                                                'dungeonscrossed'} or not world.shuffle_ganon)
    else:
        world.open_pyramid[player] = {'on': True, 'off': False, 'yes': True, 'no': False}.get(
            world.open_pyramid[player], 'auto')
        world.open_pyramid[player] = True

    world.triforce_pieces_available[player] = max(world.triforce_pieces_available[player],
                                                  world.triforce_pieces_required[player])

    if world.mode[player] != 'inverted':
        create_regions(world, player)
    else:
        create_inverted_regions(world, player)
    create_shops(world, player)
    create_dungeons(world, player)

    if world.logic[player] not in ["noglitches", "minorglitches"] and world.shuffle[player] in \
            {"vanilla", "dungeonssimple", "dungeonsfull", "simple", "restricted", "full"}:
        world.fix_fake_world[player] = False

    # seeded entrance shuffle
    old_random = world.random
    world.random = random.Random(self.er_seed)

    if world.mode[player] != 'inverted':
        link_entrances(world, player)
        from worlds.alttp_doors.memory_data.region_data import mark_light_world_regions
        mark_light_world_regions(world, player)
    else:
        link_inverted_entrances(world, player)
        from worlds.alttp_doors.legacy.inverted_regions import mark_dark_world_regions
        mark_dark_world_regions(world, player)

    world.random = old_random
    plando_connect(world, player)


def _create_region(player: int, name: str, type: RegionType, hint: str, locations=None, exits=None):
    from worlds.alttp_doors.standard.sub_classes import ALttPDoorsLocation
    ret = Region(name, type, hint, player)
    if locations is None:
        locations = []
    if exits is None:
        exits = []

    for exit in exits:
        ret.exits.append(Entrance(player, exit, ret))
    for location in locations:
        address, player_address, crystal, hint_text = location_table[location]
        ret.locations.append(ALttPDoorsLocation(player, location, address, crystal, hint_text, ret, player_address))
    return ret