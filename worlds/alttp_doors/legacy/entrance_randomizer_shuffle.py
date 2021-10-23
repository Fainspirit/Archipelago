# ToDo: With shuffle_ganon option, prevent gtower from linking to an exit only location through a 2 entrance cave.
from collections import defaultdict

from worlds.alttp_doors.legacy.rules.overworld_glitch_rules import overworld_glitch_connections
from worlds.alttp_doors.legacy.rules.underworld_glitch_rules import underworld_glitch_connections
from worlds.alttp_doors.memory_data.connection_data import mandatory_connections, default_connections, \
    default_dungeon_connections, inverted_default_connections, inverted_default_dungeon_connections, \
    inverted_mandatory_connections, Must_Exit_Invalid_Connections, Inverted_Must_Exit_Invalid_Connections
from worlds.alttp_doors.memory_data.door_data import door_addresses
from worlds.alttp_doors.memory_data.exit_data import exit_ids


def link_entrances(world, player):
    connect_two_way(world, 'Links House', 'Links House Exit', player)  # unshuffled. For now
    connect_exit(world, 'Chris Houlihan Room Exit', 'Links House',
                 player)  # should always match link's house, except for plandos

    Dungeon_Exits = Dungeon_Exits_Base.copy()
    Cave_Exits = Cave_Exits_Base.copy()
    Old_Man_House = Old_Man_House_Base.copy()
    Cave_Three_Exits = Cave_Three_Exits_Base.copy()

    unbias_some_entrances(world, Dungeon_Exits, Cave_Exits, Old_Man_House, Cave_Three_Exits)

    # setup mandatory connections
    for exitname, regionname in mandatory_connections:
        connect_simple(world, exitname, regionname, player)

    # if we do not shuffle, set default connections
    if world.shuffle[player] == 'vanilla':
        for exitname, regionname in default_connections:
            connect_simple(world, exitname, regionname, player)
        for exitname, regionname in default_dungeon_connections:
            connect_simple(world, exitname, regionname, player)
    elif world.shuffle[player] == 'dungeonssimple':
        for exitname, regionname in default_connections:
            connect_simple(world, exitname, regionname, player)

        simple_shuffle_dungeons(world, player)
    elif world.shuffle[player] == 'dungeonsfull':
        for exitname, regionname in default_connections:
            connect_simple(world, exitname, regionname, player)

        skull_woods_shuffle(world, player)

        dungeon_exits = list(Dungeon_Exits)
        lw_entrances = list(LW_Dungeon_Entrances)
        dw_entrances = list(DW_Dungeon_Entrances)

        if world.mode[player] == 'standard':
            # must connect front of hyrule castle to do escape
            connect_two_way(world, 'Hyrule Castle Entrance (South)', 'Hyrule Castle Exit (South)', player)
        else:
            dungeon_exits.append(
                ('Hyrule Castle Exit (South)', 'Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'))
            lw_entrances.append('Hyrule Castle Entrance (South)')

        if not world.shuffle_ganon:
            connect_two_way(world, 'Ganons Tower', 'Ganons Tower Exit', player)
        else:
            dw_entrances.append('Ganons Tower')
            dungeon_exits.append('Ganons Tower Exit')

        if world.mode[player] == 'standard':
            # rest of hyrule castle must be in light world, so it has to be the one connected to east exit of desert
            hyrule_castle_exits = [('Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)')]
            connect_mandatory_exits(world, lw_entrances, hyrule_castle_exits, list(LW_Dungeon_Entrances_Must_Exit),
                                    player)
            connect_caves(world, lw_entrances, [], hyrule_castle_exits, player)
        else:
            connect_mandatory_exits(world, lw_entrances, dungeon_exits, list(LW_Dungeon_Entrances_Must_Exit), player)
        connect_mandatory_exits(world, dw_entrances, dungeon_exits, list(DW_Dungeon_Entrances_Must_Exit), player)
        connect_caves(world, lw_entrances, dw_entrances, dungeon_exits, player)
    elif world.shuffle[player] == 'dungeonscrossed':
        crossed_shuffle_dungeons(world, player)
    elif world.shuffle[player] == 'simple':
        simple_shuffle_dungeons(world, player)

        old_man_entrances = list(Old_Man_Entrances)
        caves = list(Cave_Exits)
        three_exit_caves = list(Cave_Three_Exits)

        single_doors = list(Single_Cave_Doors)
        bomb_shop_doors = list(Bomb_Shop_Single_Cave_Doors)
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors)
        door_targets = list(Single_Cave_Targets)

        # we shuffle all 2 entrance caves as pairs as a start
        # start with the ones that need to be directed
        two_door_caves = list(Two_Door_Caves_Directional)
        world.random.shuffle(two_door_caves)
        world.random.shuffle(caves)
        while two_door_caves:
            entrance1, entrance2 = two_door_caves.pop()
            exit1, exit2 = caves.pop()
            connect_two_way(world, entrance1, exit1, player)
            connect_two_way(world, entrance2, exit2, player)

        # now the remaining pairs
        two_door_caves = list(Two_Door_Caves)
        world.random.shuffle(two_door_caves)
        while two_door_caves:
            entrance1, entrance2 = two_door_caves.pop()
            exit1, exit2 = caves.pop()
            connect_two_way(world, entrance1, exit1, player)
            connect_two_way(world, entrance2, exit2, player)

        # at this point only Light World death mountain entrances remain
        # place old man, has limited options
        remaining_entrances = ['Old Man Cave (West)', 'Old Man House (Bottom)', 'Death Mountain Return Cave (West)',
                               'Paradox Cave (Bottom)', 'Paradox Cave (Middle)', 'Paradox Cave (Top)',
                               'Fairy Ascension Cave (Bottom)', 'Fairy Ascension Cave (Top)', 'Spiral Cave',
                               'Spiral Cave (Bottom)']
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        remaining_entrances.extend(old_man_entrances)
        world.random.shuffle(remaining_entrances)
        old_man_entrance = remaining_entrances.pop()
        connect_two_way(world, old_man_entrance, 'Old Man Cave Exit (West)', player)
        connect_two_way(world, old_man_exit, 'Old Man Cave Exit (East)', player)

        # add old man house to ensure it is always somewhere on light death mountain
        caves.extend(list(Old_Man_House))
        caves.extend(list(three_exit_caves))

        # connect rest
        connect_caves(world, remaining_entrances, [], caves, player)

        # scramble holes
        scramble_holes(world, player)

        # place blacksmith, has limited options
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        bomb_shop_doors.extend(blacksmith_doors)

        # place bomb shop, has limited options
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Big Bomb Shop', player)
        single_doors.extend(bomb_shop_doors)

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        # place remaining doors
        connect_doors(world, single_doors, door_targets, player)
    elif world.shuffle[player] == 'restricted':
        simple_shuffle_dungeons(world, player)

        lw_entrances = list(LW_Entrances + LW_Single_Cave_Doors + Old_Man_Entrances)
        dw_entrances = list(DW_Entrances + DW_Single_Cave_Doors)
        dw_must_exits = list(DW_Entrances_Must_Exit)
        old_man_entrances = list(Old_Man_Entrances)
        caves = list(Cave_Exits + Cave_Three_Exits)

        bomb_shop_doors = list(Bomb_Shop_Single_Cave_Doors + Bomb_Shop_Multi_Cave_Doors)
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors + Blacksmith_Multi_Cave_Doors)
        door_targets = list(Single_Cave_Targets)

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        # in restricted, the only mandatory exits are in dark world
        connect_mandatory_exits(world, dw_entrances, caves, dw_must_exits, player)

        # place old man, has limited options
        # exit has to come from specific set of doors, the entrance is free to move about
        old_man_entrances = [door for door in old_man_entrances if door in lw_entrances]
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        connect_two_way(world, old_man_exit, 'Old Man Cave Exit (East)', player)
        lw_entrances.remove(old_man_exit)

        # place blacksmith, has limited options
        all_entrances = lw_entrances + dw_entrances
        # cannot place it anywhere already taken (or that are otherwise not eligable for placement)
        blacksmith_doors = [door for door in blacksmith_doors if door in all_entrances]
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        if blacksmith_hut in lw_entrances:
            lw_entrances.remove(blacksmith_hut)
        if blacksmith_hut in dw_entrances:
            dw_entrances.remove(blacksmith_hut)
        bomb_shop_doors.extend(blacksmith_doors)

        # place bomb shop, has limited options
        all_entrances = lw_entrances + dw_entrances
        # cannot place it anywhere already taken (or that are otherwise not eligable for placement)
        bomb_shop_doors = [door for door in bomb_shop_doors if door in all_entrances]
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Big Bomb Shop', player)
        if bomb_shop in lw_entrances:
            lw_entrances.remove(bomb_shop)
        if bomb_shop in dw_entrances:
            dw_entrances.remove(bomb_shop)

        # place the old man cave's entrance somewhere in the light world
        world.random.shuffle(lw_entrances)
        old_man_entrance = lw_entrances.pop()
        connect_two_way(world, old_man_entrance, 'Old Man Cave Exit (West)', player)

        # place Old Man House in Light World
        connect_caves(world, lw_entrances, [], list(Old_Man_House), player)  # for multiple seeds

        # now scramble the rest
        connect_caves(world, lw_entrances, dw_entrances, caves, player)

        # scramble holes
        scramble_holes(world, player)

        doors = lw_entrances + dw_entrances

        # place remaining doors
        connect_doors(world, doors, door_targets, player)
    elif world.shuffle[player] == 'restricted_legacy':
        simple_shuffle_dungeons(world, player)

        lw_entrances = list(LW_Entrances)
        dw_entrances = list(DW_Entrances)
        dw_must_exits = list(DW_Entrances_Must_Exit)
        old_man_entrances = list(Old_Man_Entrances)
        caves = list(Cave_Exits)
        three_exit_caves = list(Cave_Three_Exits)
        single_doors = list(Single_Cave_Doors)
        bomb_shop_doors = list(Bomb_Shop_Single_Cave_Doors)
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors)
        door_targets = list(Single_Cave_Targets)

        # only use two exit caves to do mandatory dw connections
        connect_mandatory_exits(world, dw_entrances, caves, dw_must_exits, player)
        # add three exit doors to pool for remainder
        caves.extend(three_exit_caves)

        # place old man, has limited options
        # exit has to come from specific set of doors, the entrance is free to move about
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        lw_entrances.extend(old_man_entrances)
        world.random.shuffle(lw_entrances)
        old_man_entrance = lw_entrances.pop()
        connect_two_way(world, old_man_entrance, 'Old Man Cave Exit (West)', player)
        connect_two_way(world, old_man_exit, 'Old Man Cave Exit (East)', player)

        # place Old Man House in Light World
        connect_caves(world, lw_entrances, [], Old_Man_House, player)

        # connect rest. There's 2 dw entrances remaining, so we will not run into parity issue placing caves
        connect_caves(world, lw_entrances, dw_entrances, caves, player)

        # scramble holes
        scramble_holes(world, player)

        # place blacksmith, has limited options
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        bomb_shop_doors.extend(blacksmith_doors)

        # place dam and pyramid fairy, have limited options
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Big Bomb Shop', player)
        single_doors.extend(bomb_shop_doors)

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        # place remaining doors
        connect_doors(world, single_doors, door_targets, player)
    elif world.shuffle[player] == 'full':
        skull_woods_shuffle(world, player)

        lw_entrances = list(LW_Entrances + LW_Dungeon_Entrances + LW_Single_Cave_Doors + Old_Man_Entrances)
        dw_entrances = list(DW_Entrances + DW_Dungeon_Entrances + DW_Single_Cave_Doors)
        dw_must_exits = list(DW_Entrances_Must_Exit + DW_Dungeon_Entrances_Must_Exit)
        lw_must_exits = list(LW_Dungeon_Entrances_Must_Exit)
        old_man_entrances = list(Old_Man_Entrances + ['Tower of Hera'])
        caves = list(
            Cave_Exits + Dungeon_Exits + Cave_Three_Exits)  # don't need to consider three exit caves, have one exit caves to avoid parity issues
        bomb_shop_doors = list(Bomb_Shop_Single_Cave_Doors + Bomb_Shop_Multi_Cave_Doors)
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors + Blacksmith_Multi_Cave_Doors)
        door_targets = list(Single_Cave_Targets)
        old_man_house = list(Old_Man_House)

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        if world.mode[player] == 'standard':
            # must connect front of hyrule castle to do escape
            connect_two_way(world, 'Hyrule Castle Entrance (South)', 'Hyrule Castle Exit (South)', player)
        else:
            caves.append(tuple(world.random.sample(
                ['Hyrule Castle Exit (South)', 'Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'], 3)))
            lw_entrances.append('Hyrule Castle Entrance (South)')

        if not world.shuffle_ganon:
            connect_two_way(world, 'Ganons Tower', 'Ganons Tower Exit', player)
        else:
            dw_entrances.append('Ganons Tower')
            caves.append('Ganons Tower Exit')

        # we randomize which world requirements we fulfill first so we get better dungeon distribution
        # we also places the Old Man House at this time to make sure he can be connected to the desert one way
        if world.random.randint(0, 1) == 0:
            caves += old_man_house
            connect_mandatory_exits(world, lw_entrances, caves, lw_must_exits, player)
            try:
                caves.remove(old_man_house[0])
            except ValueError:
                pass
            else:  # if the cave wasn't placed we get here
                connect_caves(world, lw_entrances, [], old_man_house, player)
            connect_mandatory_exits(world, dw_entrances, caves, dw_must_exits, player)
        else:
            connect_mandatory_exits(world, dw_entrances, caves, dw_must_exits, player)
            caves += old_man_house
            connect_mandatory_exits(world, lw_entrances, caves, lw_must_exits, player)
            try:
                caves.remove(old_man_house[0])
            except ValueError:
                pass
            else:  # if the cave wasn't placed we get here
                connect_caves(world, lw_entrances, [], old_man_house, player)
        if world.mode[player] == 'standard':
            # rest of hyrule castle must be in light world
            connect_caves(world, lw_entrances, [], [('Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)')], player)

        # place old man, has limited options
        # exit has to come from specific set of doors, the entrance is free to move about
        old_man_entrances = [door for door in old_man_entrances if door in lw_entrances]
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        connect_two_way(world, old_man_exit, 'Old Man Cave Exit (East)', player)
        lw_entrances.remove(old_man_exit)

        # place blacksmith, has limited options
        all_entrances = lw_entrances + dw_entrances
        # cannot place it anywhere already taken (or that are otherwise not eligable for placement)
        blacksmith_doors = [door for door in blacksmith_doors if door in all_entrances]
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        if blacksmith_hut in lw_entrances:
            lw_entrances.remove(blacksmith_hut)
        if blacksmith_hut in dw_entrances:
            dw_entrances.remove(blacksmith_hut)
        bomb_shop_doors.extend(blacksmith_doors)

        # place bomb shop, has limited options
        all_entrances = lw_entrances + dw_entrances
        # cannot place it anywhere already taken (or that are otherwise not eligable for placement)
        bomb_shop_doors = [door for door in bomb_shop_doors if door in all_entrances]
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Big Bomb Shop', player)
        if bomb_shop in lw_entrances:
            lw_entrances.remove(bomb_shop)
        if bomb_shop in dw_entrances:
            dw_entrances.remove(bomb_shop)

        # place the old man cave's entrance somewhere in the light world
        old_man_entrance = lw_entrances.pop()
        connect_two_way(world, old_man_entrance, 'Old Man Cave Exit (West)', player)

        # now scramble the rest
        connect_caves(world, lw_entrances, dw_entrances, caves, player)

        # scramble holes
        scramble_holes(world, player)

        doors = lw_entrances + dw_entrances

        # place remaining doors
        connect_doors(world, doors, door_targets, player)
    elif world.shuffle[player] == 'crossed':
        skull_woods_shuffle(world, player)

        entrances = list(
            LW_Entrances + LW_Dungeon_Entrances + LW_Single_Cave_Doors + Old_Man_Entrances + DW_Entrances + DW_Dungeon_Entrances + DW_Single_Cave_Doors)
        must_exits = list(DW_Entrances_Must_Exit + DW_Dungeon_Entrances_Must_Exit + LW_Dungeon_Entrances_Must_Exit)

        old_man_entrances = list(Old_Man_Entrances + ['Tower of Hera'])
        caves = list(
            Cave_Exits + Dungeon_Exits + Cave_Three_Exits + Old_Man_House)  # don't need to consider three exit caves, have one exit caves to avoid parity issues
        bomb_shop_doors = list(Bomb_Shop_Single_Cave_Doors + Bomb_Shop_Multi_Cave_Doors)
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors + Blacksmith_Multi_Cave_Doors)
        door_targets = list(Single_Cave_Targets)

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        if world.mode[player] == 'standard':
            # must connect front of hyrule castle to do escape
            connect_two_way(world, 'Hyrule Castle Entrance (South)', 'Hyrule Castle Exit (South)', player)
        else:
            caves.append(tuple(world.random.sample(
                ['Hyrule Castle Exit (South)', 'Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'], 3)))
            entrances.append('Hyrule Castle Entrance (South)')

        if not world.shuffle_ganon:
            connect_two_way(world, 'Ganons Tower', 'Ganons Tower Exit', player)
        else:
            entrances.append('Ganons Tower')
            caves.append('Ganons Tower Exit')

        # place must-exit caves
        connect_mandatory_exits(world, entrances, caves, must_exits, player)

        if world.mode[player] == 'standard':
            # rest of hyrule castle must be dealt with
            connect_caves(world, entrances, [], [('Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)')], player)

        # place old man, has limited options
        # exit has to come from specific set of doors, the entrance is free to move about
        old_man_entrances = [door for door in old_man_entrances if door in entrances]
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        connect_two_way(world, old_man_exit, 'Old Man Cave Exit (East)', player)
        entrances.remove(old_man_exit)

        # place blacksmith, has limited options
        # cannot place it anywhere already taken (or that are otherwise not eligable for placement)
        blacksmith_doors = [door for door in blacksmith_doors if door in entrances]
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        entrances.remove(blacksmith_hut)
        bomb_shop_doors.extend(blacksmith_doors)

        # place bomb shop, has limited options

        # cannot place it anywhere already taken (or that are otherwise not eligable for placement)
        bomb_shop_doors = [door for door in bomb_shop_doors if door in entrances]
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Big Bomb Shop', player)
        entrances.remove(bomb_shop)

        # place the old man cave's entrance somewhere
        world.random.shuffle(entrances)
        old_man_entrance = entrances.pop()
        connect_two_way(world, old_man_entrance, 'Old Man Cave Exit (West)', player)

        # now scramble the rest
        connect_caves(world, entrances, [], caves, player)

        # scramble holes
        scramble_holes(world, player)

        # place remaining doors
        connect_doors(world, entrances, door_targets, player)
    elif world.shuffle[player] == 'full_legacy':
        skull_woods_shuffle(world, player)

        lw_entrances = list(LW_Entrances + LW_Dungeon_Entrances + Old_Man_Entrances)
        dw_entrances = list(DW_Entrances + DW_Dungeon_Entrances)
        dw_must_exits = list(DW_Entrances_Must_Exit + DW_Dungeon_Entrances_Must_Exit)
        lw_must_exits = list(LW_Dungeon_Entrances_Must_Exit)
        old_man_entrances = list(Old_Man_Entrances + ['Tower of Hera'])
        caves = list(
            Cave_Exits + Dungeon_Exits + Cave_Three_Exits)  # don't need to consider three exit caves, have one exit caves to avoid parity issues
        single_doors = list(Single_Cave_Doors)
        bomb_shop_doors = list(Bomb_Shop_Single_Cave_Doors)
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors)
        door_targets = list(Single_Cave_Targets)

        if world.mode[player] == 'standard':
            # must connect front of hyrule castle to do escape
            connect_two_way(world, 'Hyrule Castle Entrance (South)', 'Hyrule Castle Exit (South)', player)
        else:
            caves.append(tuple(world.random.sample(
                ['Hyrule Castle Exit (South)', 'Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'], 3)))
            lw_entrances.append('Hyrule Castle Entrance (South)')

        if not world.shuffle_ganon:
            connect_two_way(world, 'Ganons Tower', 'Ganons Tower Exit', player)
        else:
            dw_entrances.append('Ganons Tower')
            caves.append('Ganons Tower Exit')

        # we randomize which world requirements we fulfill first so we get better dungeon distribution
        if world.random.randint(0, 1) == 0:
            connect_mandatory_exits(world, lw_entrances, caves, lw_must_exits, player)
            connect_mandatory_exits(world, dw_entrances, caves, dw_must_exits, player)
        else:
            connect_mandatory_exits(world, dw_entrances, caves, dw_must_exits, player)
            connect_mandatory_exits(world, lw_entrances, caves, lw_must_exits, player)
        if world.mode[player] == 'standard':
            # rest of hyrule castle must be in light world
            connect_caves(world, lw_entrances, [], [('Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)')], player)

        # place old man, has limited options
        # exit has to come from specific set of doors, the entrance is free to move about
        old_man_entrances = [door for door in old_man_entrances if door in lw_entrances]
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        lw_entrances.remove(old_man_exit)

        world.random.shuffle(lw_entrances)
        old_man_entrance = lw_entrances.pop()
        connect_two_way(world, old_man_entrance, 'Old Man Cave Exit (West)', player)
        connect_two_way(world, old_man_exit, 'Old Man Cave Exit (East)', player)

        # place Old Man House in Light World
        connect_caves(world, lw_entrances, [], list(Old_Man_House),
                      player)  # need this to avoid badness with multiple seeds

        # now scramble the rest
        connect_caves(world, lw_entrances, dw_entrances, caves, player)

        # scramble holes
        scramble_holes(world, player)

        # place blacksmith, has limited options
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        bomb_shop_doors.extend(blacksmith_doors)

        # place bomb shop, has limited options
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Big Bomb Shop', player)
        single_doors.extend(bomb_shop_doors)

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        # place remaining doors
        connect_doors(world, single_doors, door_targets, player)
    elif world.shuffle[player] == 'madness_legacy':
        # here lie dragons, connections are no longer two way
        lw_entrances = list(LW_Entrances + LW_Dungeon_Entrances + Old_Man_Entrances)
        dw_entrances = list(DW_Entrances + DW_Dungeon_Entrances)
        dw_entrances_must_exits = list(DW_Entrances_Must_Exit + DW_Dungeon_Entrances_Must_Exit)

        lw_doors = list(LW_Entrances + LW_Dungeon_Entrances + LW_Dungeon_Entrances_Must_Exit) + ['Kakariko Well Cave',
                                                                                                 'Bat Cave Cave',
                                                                                                 'North Fairy Cave',
                                                                                                 'Sanctuary',
                                                                                                 'Lost Woods Hideout Stump',
                                                                                                 'Lumberjack Tree Cave'] + list(
            Old_Man_Entrances)
        dw_doors = list(
            DW_Entrances + DW_Dungeon_Entrances + DW_Entrances_Must_Exit + DW_Dungeon_Entrances_Must_Exit) + [
                       'Skull Woods First Section Door', 'Skull Woods Second Section Door (East)',
                       'Skull Woods Second Section Door (West)']

        world.random.shuffle(lw_doors)
        world.random.shuffle(dw_doors)

        dw_entrances_must_exits.append('Skull Woods Second Section Door (West)')
        dw_entrances.append('Skull Woods Second Section Door (East)')
        dw_entrances.append('Skull Woods First Section Door')

        lw_entrances.extend(
            ['Kakariko Well Cave', 'Bat Cave Cave', 'North Fairy Cave', 'Sanctuary', 'Lost Woods Hideout Stump',
             'Lumberjack Tree Cave'])

        lw_entrances_must_exits = list(LW_Dungeon_Entrances_Must_Exit)

        old_man_entrances = list(Old_Man_Entrances) + ['Tower of Hera']

        mandatory_light_world = ['Old Man House Exit (Bottom)', 'Old Man House Exit (Top)']
        mandatory_dark_world = []
        caves = list(Cave_Exits + Dungeon_Exits + Cave_Three_Exits)

        # shuffle up holes

        lw_hole_entrances = ['Kakariko Well Drop', 'Bat Cave Drop', 'North Fairy Cave Drop', 'Lost Woods Hideout Drop',
                             'Lumberjack Tree Tree', 'Sanctuary Grave']
        dw_hole_entrances = ['Skull Woods First Section Hole (East)', 'Skull Woods First Section Hole (West)',
                             'Skull Woods First Section Hole (North)', 'Skull Woods Second Section Hole']

        hole_targets = [('Kakariko Well Exit', 'Kakariko Well (top)'),
                        ('Bat Cave Exit', 'Bat Cave (right)'),
                        ('North Fairy Cave Exit', 'North Fairy Cave'),
                        ('Lost Woods Hideout Exit', 'Lost Woods Hideout (top)'),
                        ('Lumberjack Tree Exit', 'Lumberjack Tree (top)'),
                        (('Skull Woods Second Section Exit (East)', 'Skull Woods Second Section Exit (West)'),
                         'Skull Woods Second Section (Drop)')]

        if world.mode[player] == 'standard':
            # cannot move uncle cave
            connect_entrance(world, 'Hyrule Castle Secret Entrance Drop', 'Hyrule Castle Secret Entrance', player)
            connect_exit(world, 'Hyrule Castle Secret Entrance Exit', 'Hyrule Castle Secret Entrance Stairs', player)
            connect_entrance(world, 'Hyrule Castle Secret Entrance Stairs', 'Hyrule Castle Secret Entrance Exit',
                             player)
        else:
            lw_hole_entrances.append('Hyrule Castle Secret Entrance Drop')
            hole_targets.append(('Hyrule Castle Secret Entrance Exit', 'Hyrule Castle Secret Entrance'))
            lw_doors.append('Hyrule Castle Secret Entrance Stairs')
            lw_entrances.append('Hyrule Castle Secret Entrance Stairs')

        if not world.shuffle_ganon:
            connect_two_way(world, 'Ganons Tower', 'Ganons Tower Exit', player)
            connect_two_way(world, 'Pyramid Entrance', 'Pyramid Exit', player)
            connect_entrance(world, 'Pyramid Hole', 'Pyramid', player)
        else:
            dw_entrances.append('Ganons Tower')
            caves.append('Ganons Tower Exit')
            dw_hole_entrances.append('Pyramid Hole')
            hole_targets.append(('Pyramid Exit', 'Pyramid'))
            dw_entrances_must_exits.append('Pyramid Entrance')
            dw_doors.extend(['Ganons Tower', 'Pyramid Entrance'])

        world.random.shuffle(lw_hole_entrances)
        world.random.shuffle(dw_hole_entrances)
        world.random.shuffle(hole_targets)

        # decide if skull woods first section should be in light or dark world
        sw_light = world.random.randint(0, 1) == 0
        if sw_light:
            sw_hole_pool = lw_hole_entrances
            mandatory_light_world.append('Skull Woods First Section Exit')
        else:
            sw_hole_pool = dw_hole_entrances
            mandatory_dark_world.append('Skull Woods First Section Exit')
        for target in ['Skull Woods First Section (Left)', 'Skull Woods First Section (Right)',
                       'Skull Woods First Section (Top)']:
            connect_entrance(world, sw_hole_pool.pop(), target, player)

        # sanctuary has to be in light world
        connect_entrance(world, lw_hole_entrances.pop(), 'Sewer Drop', player)
        mandatory_light_world.append('Sanctuary Exit')

        # fill up remaining holes
        for hole in dw_hole_entrances:
            exits, target = hole_targets.pop()
            mandatory_dark_world.append(exits)
            connect_entrance(world, hole, target, player)

        for hole in lw_hole_entrances:
            exits, target = hole_targets.pop()
            mandatory_light_world.append(exits)
            connect_entrance(world, hole, target, player)

        # hyrule castle handling
        if world.mode[player] == 'standard':
            # must connect front of hyrule castle to do escape
            connect_entrance(world, 'Hyrule Castle Entrance (South)', 'Hyrule Castle Exit (South)', player)
            connect_exit(world, 'Hyrule Castle Exit (South)', 'Hyrule Castle Entrance (South)', player)
            mandatory_light_world.append(('Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'))
        else:
            lw_doors.append('Hyrule Castle Entrance (South)')
            lw_entrances.append('Hyrule Castle Entrance (South)')
            caves.append(('Hyrule Castle Exit (South)', 'Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'))

        # now let's deal with mandatory reachable stuff
        def extract_reachable_exit(cavelist):
            world.random.shuffle(cavelist)
            candidate = None
            for cave in cavelist:
                if isinstance(cave, tuple) and len(cave) > 1:
                    # special handling: TRock and Spectracle Rock cave have two entries that we should consider entrance only
                    # ToDo this should be handled in a more sensible manner
                    if cave[0] in ['Turtle Rock Exit (Front)', 'Spectacle Rock Cave Exit (Peak)'] and len(cave) == 2:
                        continue
                    candidate = cave
                    break
            if candidate is None:
                raise KeyError('No suitable cave.')
            cavelist.remove(candidate)
            return candidate

        def connect_reachable_exit(entrance, general, worldspecific, worldoors):
            # select which one is the primary option
            if world.random.randint(0, 1) == 0:
                primary = general
                secondary = worldspecific
            else:
                primary = worldspecific
                secondary = general

            try:
                cave = extract_reachable_exit(primary)
            except KeyError:
                cave = extract_reachable_exit(secondary)

            exit = cave[-1]
            cave = cave[:-1]
            connect_exit(world, exit, entrance, player)
            connect_entrance(world, worldoors.pop(), exit, player)
            # rest of cave now is forced to be in this world
            worldspecific.append(cave)

        # we randomize which world requirements we fulfill first so we get better dungeon distribution
        if world.random.randint(0, 1) == 0:
            for entrance in lw_entrances_must_exits:
                connect_reachable_exit(entrance, caves, mandatory_light_world, lw_doors)
            for entrance in dw_entrances_must_exits:
                connect_reachable_exit(entrance, caves, mandatory_dark_world, dw_doors)
        else:
            for entrance in dw_entrances_must_exits:
                connect_reachable_exit(entrance, caves, mandatory_dark_world, dw_doors)
            for entrance in lw_entrances_must_exits:
                connect_reachable_exit(entrance, caves, mandatory_light_world, lw_doors)

        # place old man, has limited options
        # exit has to come from specific set of doors, the entrance is free to move about
        old_man_entrances = [entrance for entrance in old_man_entrances if entrance in lw_entrances]
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        lw_entrances.remove(old_man_exit)

        connect_exit(world, 'Old Man Cave Exit (East)', old_man_exit, player)
        connect_entrance(world, lw_doors.pop(), 'Old Man Cave Exit (East)', player)
        mandatory_light_world.append('Old Man Cave Exit (West)')

        # we connect up the mandatory associations we have found
        for mandatory in mandatory_light_world:
            if not isinstance(mandatory, tuple):
                mandatory = (mandatory,)
            for exit in mandatory:
                # point out somewhere
                connect_exit(world, exit, lw_entrances.pop(), player)
                # point in from somewhere
                connect_entrance(world, lw_doors.pop(), exit, player)

        for mandatory in mandatory_dark_world:
            if not isinstance(mandatory, tuple):
                mandatory = (mandatory,)
            for exit in mandatory:
                # point out somewhere
                connect_exit(world, exit, dw_entrances.pop(), player)
                # point in from somewhere
                connect_entrance(world, dw_doors.pop(), exit, player)

        # handle remaining caves
        while caves:
            # connect highest exit count caves first, prevent issue where we have 2 or 3 exits accross worlds left to fill
            cave_candidate = (None, 0)
            for i, cave in enumerate(caves):
                if isinstance(cave, str):
                    cave = (cave,)
                if len(cave) > cave_candidate[1]:
                    cave_candidate = (i, len(cave))
            cave = caves.pop(cave_candidate[0])

            place_lightworld = world.random.randint(0, 1) == 0
            if place_lightworld:
                target_doors = lw_doors
                target_entrances = lw_entrances
            else:
                target_doors = dw_doors
                target_entrances = dw_entrances

            if isinstance(cave, str):
                cave = (cave,)

            # check if we can still fit the cave into our target group
            if len(target_doors) < len(cave):
                if not place_lightworld:
                    target_doors = lw_doors
                    target_entrances = lw_entrances
                else:
                    target_doors = dw_doors
                    target_entrances = dw_entrances

            for exit in cave:
                connect_exit(world, exit, target_entrances.pop(), player)
                connect_entrance(world, target_doors.pop(), exit, player)

        # handle simple doors

        single_doors = list(Single_Cave_Doors)
        bomb_shop_doors = list(Bomb_Shop_Single_Cave_Doors)
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors)
        door_targets = list(Single_Cave_Targets)

        # place blacksmith, has limited options
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        bomb_shop_doors.extend(blacksmith_doors)

        # place dam and pyramid fairy, have limited options
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Big Bomb Shop', player)
        single_doors.extend(bomb_shop_doors)

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        # place remaining doors
        connect_doors(world, single_doors, door_targets, player)
    elif world.shuffle[player] == 'insanity':
        # beware ye who enter here

        entrances = LW_Entrances + LW_Dungeon_Entrances + DW_Entrances + DW_Dungeon_Entrances + Old_Man_Entrances + [
            'Skull Woods Second Section Door (East)', 'Skull Woods First Section Door', 'Kakariko Well Cave',
            'Bat Cave Cave', 'North Fairy Cave', 'Sanctuary', 'Lost Woods Hideout Stump', 'Lumberjack Tree Cave']
        entrances_must_exits = DW_Entrances_Must_Exit + DW_Dungeon_Entrances_Must_Exit + LW_Dungeon_Entrances_Must_Exit + [
            'Skull Woods Second Section Door (West)']

        doors = LW_Entrances + LW_Dungeon_Entrances + LW_Dungeon_Entrances_Must_Exit + ['Kakariko Well Cave',
                                                                                        'Bat Cave Cave',
                                                                                        'North Fairy Cave', 'Sanctuary',
                                                                                        'Lost Woods Hideout Stump',
                                                                                        'Lumberjack Tree Cave'] + Old_Man_Entrances + \
                DW_Entrances + DW_Dungeon_Entrances + DW_Entrances_Must_Exit + DW_Dungeon_Entrances_Must_Exit + [
                    'Skull Woods First Section Door', 'Skull Woods Second Section Door (East)',
                    'Skull Woods Second Section Door (West)'] + \
                LW_Single_Cave_Doors + DW_Single_Cave_Doors

        # TODO: there are other possible entrances we could support here by way of exiting from a connector,
        # and rentering to find bomb shop. However appended list here is all those that we currently have
        # bomb shop logic for.
        # Specifically we could potentially add: 'Dark Death Mountain Ledge (East)' and doors associated with pits
        bomb_shop_doors = list(
            Bomb_Shop_Single_Cave_Doors + Bomb_Shop_Multi_Cave_Doors + ['Desert Palace Entrance (East)',
                                                                        'Turtle Rock Isolated Ledge Entrance',
                                                                        'Bumper Cave (Top)',
                                                                        'Hookshot Cave Back Entrance'])
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors + Blacksmith_Multi_Cave_Doors)
        door_targets = list(Single_Cave_Targets)

        world.random.shuffle(doors)

        old_man_entrances = list(Old_Man_Entrances) + ['Tower of Hera']

        caves = Cave_Exits + Dungeon_Exits + Cave_Three_Exits + ['Old Man House Exit (Bottom)',
                                                                 'Old Man House Exit (Top)',
                                                                 'Skull Woods First Section Exit',
                                                                 'Skull Woods Second Section Exit (East)',
                                                                 'Skull Woods Second Section Exit (West)',
                                                                 'Kakariko Well Exit', 'Bat Cave Exit',
                                                                 'North Fairy Cave Exit', 'Lost Woods Hideout Exit',
                                                                 'Lumberjack Tree Exit', 'Sanctuary Exit']

        # shuffle up holes

        hole_entrances = ['Kakariko Well Drop', 'Bat Cave Drop', 'North Fairy Cave Drop', 'Lost Woods Hideout Drop',
                          'Lumberjack Tree Tree', 'Sanctuary Grave',
                          'Skull Woods First Section Hole (East)', 'Skull Woods First Section Hole (West)',
                          'Skull Woods First Section Hole (North)', 'Skull Woods Second Section Hole']

        hole_targets = ['Kakariko Well (top)', 'Bat Cave (right)', 'North Fairy Cave', 'Lost Woods Hideout (top)',
                        'Lumberjack Tree (top)', 'Sewer Drop', 'Skull Woods Second Section (Drop)',
                        'Skull Woods First Section (Left)', 'Skull Woods First Section (Right)',
                        'Skull Woods First Section (Top)']

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        if world.mode[player] == 'standard':
            # cannot move uncle cave
            connect_entrance(world, 'Hyrule Castle Secret Entrance Drop', 'Hyrule Castle Secret Entrance', player)
            connect_exit(world, 'Hyrule Castle Secret Entrance Exit', 'Hyrule Castle Secret Entrance Stairs', player)
            connect_entrance(world, 'Hyrule Castle Secret Entrance Stairs', 'Hyrule Castle Secret Entrance Exit',
                             player)
        else:
            hole_entrances.append('Hyrule Castle Secret Entrance Drop')
            hole_targets.append('Hyrule Castle Secret Entrance')
            doors.append('Hyrule Castle Secret Entrance Stairs')
            entrances.append('Hyrule Castle Secret Entrance Stairs')
            caves.append('Hyrule Castle Secret Entrance Exit')

        if not world.shuffle_ganon:
            connect_two_way(world, 'Ganons Tower', 'Ganons Tower Exit', player)
            connect_two_way(world, 'Pyramid Entrance', 'Pyramid Exit', player)
            connect_entrance(world, 'Pyramid Hole', 'Pyramid', player)
        else:
            entrances.append('Ganons Tower')
            caves.extend(['Ganons Tower Exit', 'Pyramid Exit'])
            hole_entrances.append('Pyramid Hole')
            hole_targets.append('Pyramid')
            entrances_must_exits.append('Pyramid Entrance')
            doors.extend(['Ganons Tower', 'Pyramid Entrance'])

        world.random.shuffle(hole_entrances)
        world.random.shuffle(hole_targets)
        world.random.shuffle(entrances)

        # fill up holes
        for hole in hole_entrances:
            connect_entrance(world, hole, hole_targets.pop(), player)

        # hyrule castle handling
        if world.mode[player] == 'standard':
            # must connect front of hyrule castle to do escape
            connect_entrance(world, 'Hyrule Castle Entrance (South)', 'Hyrule Castle Exit (South)', player)
            connect_exit(world, 'Hyrule Castle Exit (South)', 'Hyrule Castle Entrance (South)', player)
            caves.append(('Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'))
        else:
            doors.append('Hyrule Castle Entrance (South)')
            entrances.append('Hyrule Castle Entrance (South)')
            caves.append(('Hyrule Castle Exit (South)', 'Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'))

        # now let's deal with mandatory reachable stuff
        def extract_reachable_exit(cavelist):
            world.random.shuffle(cavelist)
            candidate = None
            for cave in cavelist:
                if isinstance(cave, tuple) and len(cave) > 1:
                    # special handling: TRock has two entries that we should consider entrance only
                    # ToDo this should be handled in a more sensible manner
                    if cave[0] in ['Turtle Rock Exit (Front)', 'Spectacle Rock Cave Exit (Peak)'] and len(cave) == 2:
                        continue
                    candidate = cave
                    break
            if candidate is None:
                raise KeyError('No suitable cave.')
            cavelist.remove(candidate)
            return candidate

        def connect_reachable_exit(entrance, caves, doors):
            cave = extract_reachable_exit(caves)

            exit = cave[-1]
            cave = cave[:-1]
            connect_exit(world, exit, entrance, player)
            connect_entrance(world, doors.pop(), exit, player)
            # rest of cave now is forced to be in this world
            caves.append(cave)

        # connect mandatory exits
        for entrance in entrances_must_exits:
            connect_reachable_exit(entrance, caves, doors)

        # place old man, has limited options
        # exit has to come from specific set of doors, the entrance is free to move about
        old_man_entrances = [entrance for entrance in old_man_entrances if entrance in entrances]
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        entrances.remove(old_man_exit)

        connect_exit(world, 'Old Man Cave Exit (East)', old_man_exit, player)
        connect_entrance(world, doors.pop(), 'Old Man Cave Exit (East)', player)
        caves.append('Old Man Cave Exit (West)')

        # place blacksmith, has limited options
        blacksmith_doors = [door for door in blacksmith_doors if door in doors]
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        doors.remove(blacksmith_hut)

        # place dam and pyramid fairy, have limited options
        bomb_shop_doors = [door for door in bomb_shop_doors if door in doors]
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Big Bomb Shop', player)
        doors.remove(bomb_shop)

        # handle remaining caves
        for cave in caves:
            if isinstance(cave, str):
                cave = (cave,)

            for exit in cave:
                connect_exit(world, exit, entrances.pop(), player)
                connect_entrance(world, doors.pop(), exit, player)

        # place remaining doors
        connect_doors(world, doors, door_targets, player)
    elif world.shuffle[player] == 'insanity_legacy':
        world.fix_fake_world[player] = False
        # beware ye who enter here

        entrances = LW_Entrances + LW_Dungeon_Entrances + DW_Entrances + DW_Dungeon_Entrances + Old_Man_Entrances + [
            'Skull Woods Second Section Door (East)', 'Skull Woods First Section Door', 'Kakariko Well Cave',
            'Bat Cave Cave', 'North Fairy Cave', 'Sanctuary', 'Lost Woods Hideout Stump', 'Lumberjack Tree Cave']
        entrances_must_exits = DW_Entrances_Must_Exit + DW_Dungeon_Entrances_Must_Exit + LW_Dungeon_Entrances_Must_Exit + [
            'Skull Woods Second Section Door (West)']

        doors = LW_Entrances + LW_Dungeon_Entrances + LW_Dungeon_Entrances_Must_Exit + ['Kakariko Well Cave',
                                                                                        'Bat Cave Cave',
                                                                                        'North Fairy Cave', 'Sanctuary',
                                                                                        'Lost Woods Hideout Stump',
                                                                                        'Lumberjack Tree Cave'] + Old_Man_Entrances + \
                DW_Entrances + DW_Dungeon_Entrances + DW_Entrances_Must_Exit + DW_Dungeon_Entrances_Must_Exit + [
                    'Skull Woods First Section Door', 'Skull Woods Second Section Door (East)',
                    'Skull Woods Second Section Door (West)']

        world.random.shuffle(doors)

        old_man_entrances = list(Old_Man_Entrances) + ['Tower of Hera']

        caves = Cave_Exits + Dungeon_Exits + Cave_Three_Exits + ['Old Man House Exit (Bottom)',
                                                                 'Old Man House Exit (Top)',
                                                                 'Skull Woods First Section Exit',
                                                                 'Skull Woods Second Section Exit (East)',
                                                                 'Skull Woods Second Section Exit (West)',
                                                                 'Kakariko Well Exit', 'Bat Cave Exit',
                                                                 'North Fairy Cave Exit', 'Lost Woods Hideout Exit',
                                                                 'Lumberjack Tree Exit', 'Sanctuary Exit']

        # shuffle up holes

        hole_entrances = ['Kakariko Well Drop', 'Bat Cave Drop', 'North Fairy Cave Drop', 'Lost Woods Hideout Drop',
                          'Lumberjack Tree Tree', 'Sanctuary Grave',
                          'Skull Woods First Section Hole (East)', 'Skull Woods First Section Hole (West)',
                          'Skull Woods First Section Hole (North)', 'Skull Woods Second Section Hole']

        hole_targets = ['Kakariko Well (top)', 'Bat Cave (right)', 'North Fairy Cave', 'Lost Woods Hideout (top)',
                        'Lumberjack Tree (top)', 'Sewer Drop', 'Skull Woods Second Section (Drop)',
                        'Skull Woods First Section (Left)', 'Skull Woods First Section (Right)',
                        'Skull Woods First Section (Top)']

        if world.mode[player] == 'standard':
            # cannot move uncle cave
            connect_entrance(world, 'Hyrule Castle Secret Entrance Drop', 'Hyrule Castle Secret Entrance', player)
            connect_exit(world, 'Hyrule Castle Secret Entrance Exit', 'Hyrule Castle Secret Entrance Stairs', player)
            connect_entrance(world, 'Hyrule Castle Secret Entrance Stairs', 'Hyrule Castle Secret Entrance Exit',
                             player)
        else:
            hole_entrances.append('Hyrule Castle Secret Entrance Drop')
            hole_targets.append('Hyrule Castle Secret Entrance')
            doors.append('Hyrule Castle Secret Entrance Stairs')
            entrances.append('Hyrule Castle Secret Entrance Stairs')
            caves.append('Hyrule Castle Secret Entrance Exit')

        if not world.shuffle_ganon:
            connect_two_way(world, 'Ganons Tower', 'Ganons Tower Exit', player)
            connect_two_way(world, 'Pyramid Entrance', 'Pyramid Exit', player)
            connect_entrance(world, 'Pyramid Hole', 'Pyramid', player)
        else:
            entrances.append('Ganons Tower')
            caves.extend(['Ganons Tower Exit', 'Pyramid Exit'])
            hole_entrances.append('Pyramid Hole')
            hole_targets.append('Pyramid')
            entrances_must_exits.append('Pyramid Entrance')
            doors.extend(['Ganons Tower', 'Pyramid Entrance'])

        world.random.shuffle(hole_entrances)
        world.random.shuffle(hole_targets)
        world.random.shuffle(entrances)

        # fill up holes
        for hole in hole_entrances:
            connect_entrance(world, hole, hole_targets.pop(), player)

        # hyrule castle handling
        if world.mode[player] == 'standard':
            # must connect front of hyrule castle to do escape
            connect_entrance(world, 'Hyrule Castle Entrance (South)', 'Hyrule Castle Exit (South)', player)
            connect_exit(world, 'Hyrule Castle Exit (South)', 'Hyrule Castle Entrance (South)', player)
            caves.append(('Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'))
        else:
            doors.append('Hyrule Castle Entrance (South)')
            entrances.append('Hyrule Castle Entrance (South)')
            caves.append(('Hyrule Castle Exit (South)', 'Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'))

        # now let's deal with mandatory reachable stuff
        def extract_reachable_exit(cavelist):
            world.random.shuffle(cavelist)
            candidate = None
            for cave in cavelist:
                if isinstance(cave, tuple) and len(cave) > 1:
                    # special handling: TRock has two entries that we should consider entrance only
                    # ToDo this should be handled in a more sensible manner
                    if cave[0] in ['Turtle Rock Exit (Front)', 'Spectacle Rock Cave Exit (Peak)'] and len(cave) == 2:
                        continue
                    candidate = cave
                    break
            if candidate is None:
                raise KeyError('No suitable cave.')
            cavelist.remove(candidate)
            return candidate

        def connect_reachable_exit(entrance, caves, doors):
            cave = extract_reachable_exit(caves)

            exit = cave[-1]
            cave = cave[:-1]
            connect_exit(world, exit, entrance, player)
            connect_entrance(world, doors.pop(), exit, player)
            # rest of cave now is forced to be in this world
            caves.append(cave)

        # connect mandatory exits
        for entrance in entrances_must_exits:
            connect_reachable_exit(entrance, caves, doors)

        # place old man, has limited options
        # exit has to come from specific set of doors, the entrance is free to move about
        old_man_entrances = [entrance for entrance in old_man_entrances if entrance in entrances]
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        entrances.remove(old_man_exit)

        connect_exit(world, 'Old Man Cave Exit (East)', old_man_exit, player)
        connect_entrance(world, doors.pop(), 'Old Man Cave Exit (East)', player)
        caves.append('Old Man Cave Exit (West)')

        # handle remaining caves
        for cave in caves:
            if isinstance(cave, str):
                cave = (cave,)

            for exit in cave:
                connect_exit(world, exit, entrances.pop(), player)
                connect_entrance(world, doors.pop(), exit, player)

        # handle simple doors

        single_doors = list(Single_Cave_Doors)
        bomb_shop_doors = list(Bomb_Shop_Single_Cave_Doors)
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors)
        door_targets = list(Single_Cave_Targets)

        # place blacksmith, has limited options
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        bomb_shop_doors.extend(blacksmith_doors)

        # place dam and pyramid fairy, have limited options
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Big Bomb Shop', player)
        single_doors.extend(bomb_shop_doors)

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        # place remaining doors
        connect_doors(world, single_doors, door_targets, player)
    else:
        raise NotImplementedError(
            f'{world.shuffle[player]} Shuffling not supported yet. Player {world.get_player_name(player)}')

    if world.logic[player] in ['owglitches', 'hybridglitches', 'nologic']:
        overworld_glitch_connections(world, player)
        # mandatory hybrid major glitches connections
        if world.logic[player] in ['hybridglitches', 'nologic']:
            underworld_glitch_connections(world, player)

    # check for swamp palace fix
    if world.get_entrance('Dam', player).connected_region.name != 'Dam' or world.get_entrance('Swamp Palace',
                                                                                              player).connected_region.name != 'Swamp Palace (Entrance)':
        world.swamp_patch_required[player] = True

    # check for potion shop location
    if world.get_entrance('Potion Shop', player).connected_region.name != 'Potion Shop':
        world.powder_patch_required[player] = True

    # check for ganon location
    if world.get_entrance('Pyramid Hole', player).connected_region.name != 'Pyramid':
        world.ganon_at_pyramid[player] = False

    # check for Ganon's Tower location
    if world.get_entrance('Ganons Tower', player).connected_region.name != 'Ganons Tower (Entrance)':
        world.ganonstower_vanilla[player] = False


def link_inverted_entrances(world, player):
    # Link's house shuffled freely, Houlihan set in mandatory_connections

    Dungeon_Exits = Inverted_Dungeon_Exits_Base.copy()
    Cave_Exits = Cave_Exits_Base.copy()
    Old_Man_House = Old_Man_House_Base.copy()
    Cave_Three_Exits = Cave_Three_Exits_Base.copy()

    unbias_some_entrances(world, Dungeon_Exits, Cave_Exits, Old_Man_House, Cave_Three_Exits)

    # setup mandatory connections
    for exitname, regionname in inverted_mandatory_connections:
        connect_simple(world, exitname, regionname, player)

    # if we do not shuffle, set default connections
    if world.shuffle[player] == 'vanilla':
        for exitname, regionname in inverted_default_connections:
            connect_simple(world, exitname, regionname, player)
        for exitname, regionname in inverted_default_dungeon_connections:
            connect_simple(world, exitname, regionname, player)
    elif world.shuffle[player] == 'dungeonssimple':
        for exitname, regionname in inverted_default_connections:
            connect_simple(world, exitname, regionname, player)

        simple_shuffle_dungeons(world, player)
    elif world.shuffle[player] == 'dungeonsfull':
        for exitname, regionname in inverted_default_connections:
            connect_simple(world, exitname, regionname, player)

        skull_woods_shuffle(world, player)

        dungeon_exits = list(Dungeon_Exits)
        lw_entrances = list(Inverted_LW_Dungeon_Entrances)
        lw_dungeon_entrances_must_exit = list(Inverted_LW_Dungeon_Entrances_Must_Exit)
        dw_entrances = list(Inverted_DW_Dungeon_Entrances)

        # randomize which desert ledge door is a must-exit
        if world.random.randint(0, 1):
            lw_dungeon_entrances_must_exit.append('Desert Palace Entrance (North)')
            lw_entrances.append('Desert Palace Entrance (West)')
        else:
            lw_dungeon_entrances_must_exit.append('Desert Palace Entrance (West)')
            lw_entrances.append('Desert Palace Entrance (North)')

        dungeon_exits.append(('Hyrule Castle Exit (South)', 'Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'))
        lw_entrances.append('Hyrule Castle Entrance (South)')

        if not world.shuffle_ganon:
            connect_two_way(world, 'Inverted Ganons Tower', 'Inverted Ganons Tower Exit', player)
            hc_ledge_entrances = ['Hyrule Castle Entrance (West)', 'Hyrule Castle Entrance (East)']
        else:
            lw_entrances.append('Inverted Ganons Tower')
            dungeon_exits.append('Inverted Ganons Tower Exit')
            hc_ledge_entrances = ['Hyrule Castle Entrance (West)', 'Hyrule Castle Entrance (East)',
                                  'Inverted Ganons Tower']

        # shuffle aga door first. If it's on HC ledge, remaining HC ledge door must be must-exit
        all_entrances_aga = lw_entrances + dw_entrances
        aga_doors = [i for i in all_entrances_aga]
        world.random.shuffle(aga_doors)
        aga_door = aga_doors.pop()

        if aga_door in hc_ledge_entrances:
            lw_entrances.remove(aga_door)
            hc_ledge_entrances.remove(aga_door)

            world.random.shuffle(hc_ledge_entrances)
            hc_ledge_must_exit = hc_ledge_entrances.pop()
            lw_entrances.remove(hc_ledge_must_exit)
            lw_dungeon_entrances_must_exit.append(hc_ledge_must_exit)
        elif aga_door in lw_entrances:
            lw_entrances.remove(aga_door)
        else:
            dw_entrances.remove(aga_door)

        connect_two_way(world, aga_door, 'Inverted Agahnims Tower Exit', player)
        dungeon_exits.remove('Inverted Agahnims Tower Exit')

        connect_mandatory_exits(world, lw_entrances, dungeon_exits, lw_dungeon_entrances_must_exit, player)

        connect_caves(world, lw_entrances, dw_entrances, dungeon_exits, player)
    elif world.shuffle[player] == 'dungeonscrossed':
        inverted_crossed_shuffle_dungeons(world, player)
    elif world.shuffle[player] == 'simple':
        simple_shuffle_dungeons(world, player)

        old_man_entrances = list(Inverted_Old_Man_Entrances)
        caves = list(Cave_Exits)
        three_exit_caves = list(Cave_Three_Exits)

        single_doors = list(Single_Cave_Doors)
        bomb_shop_doors = list(Inverted_Bomb_Shop_Single_Cave_Doors)
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors)
        door_targets = list(Inverted_Single_Cave_Targets)

        # we shuffle all 2 entrance caves as pairs as a start
        # start with the ones that need to be directed
        two_door_caves = list(Inverted_Two_Door_Caves_Directional)
        world.random.shuffle(two_door_caves)
        world.random.shuffle(caves)
        while two_door_caves:
            entrance1, entrance2 = two_door_caves.pop()
            exit1, exit2 = caves.pop()
            connect_two_way(world, entrance1, exit1, player)
            connect_two_way(world, entrance2, exit2, player)

        # now the remaining pairs
        two_door_caves = list(Inverted_Two_Door_Caves)
        world.random.shuffle(two_door_caves)
        while two_door_caves:
            entrance1, entrance2 = two_door_caves.pop()
            exit1, exit2 = caves.pop()
            connect_two_way(world, entrance1, exit1, player)
            connect_two_way(world, entrance2, exit2, player)

        # place links house
        links_house_doors = [i for i in bomb_shop_doors + blacksmith_doors if
                             i not in Inverted_Dark_Sanctuary_Doors + Isolated_LH_Doors]
        links_house = world.random.choice(list(links_house_doors))
        connect_two_way(world, links_house, 'Inverted Links House Exit', player)
        if links_house in bomb_shop_doors:
            bomb_shop_doors.remove(links_house)
        if links_house in blacksmith_doors:
            blacksmith_doors.remove(links_house)
        if links_house in old_man_entrances:
            old_man_entrances.remove(links_house)

        # place dark sanc
        sanc_doors = [door for door in Inverted_Dark_Sanctuary_Doors if door in bomb_shop_doors]
        sanc_door = world.random.choice(sanc_doors)
        bomb_shop_doors.remove(sanc_door)

        connect_entrance(world, sanc_door, 'Inverted Dark Sanctuary', player)
        world.get_entrance('Inverted Dark Sanctuary Exit', player).connect(
            world.get_entrance(sanc_door, player).parent_region)

        lw_dm_entrances = ['Paradox Cave (Bottom)', 'Paradox Cave (Middle)', 'Paradox Cave (Top)',
                           'Old Man House (Bottom)',
                           'Fairy Ascension Cave (Bottom)', 'Fairy Ascension Cave (Top)', 'Spiral Cave (Bottom)',
                           'Old Man Cave (East)',
                           'Death Mountain Return Cave (East)', 'Spiral Cave', 'Old Man House (Top)',
                           'Spectacle Rock Cave',
                           'Spectacle Rock Cave Peak', 'Spectacle Rock Cave (Bottom)']

        # place old man, bumper cave bottom to DDM entrances not in east bottom

        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        connect_two_way(world, 'Bumper Cave (Bottom)', 'Old Man Cave Exit (West)', player)
        connect_two_way(world, old_man_exit, 'Old Man Cave Exit (East)', player)
        if old_man_exit == 'Spike Cave':
            bomb_shop_doors.remove('Spike Cave')
            bomb_shop_doors.extend(old_man_entrances)

        # add old man house to ensure it is always somewhere on light death mountain
        caves.extend(list(Old_Man_House))
        caves.extend(list(three_exit_caves))

        # connect rest
        connect_caves(world, lw_dm_entrances, [], caves, player)

        # scramble holes
        scramble_inverted_holes(world, player)

        # place blacksmith, has limited options
        blacksmith_doors = [door for door in blacksmith_doors[:]]
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        bomb_shop_doors.extend(blacksmith_doors)

        # place bomb shop, has limited options
        bomb_shop_doors = [door for door in bomb_shop_doors[:]]
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Inverted Big Bomb Shop', player)
        single_doors.extend(bomb_shop_doors)

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        # place remaining doors
        connect_doors(world, single_doors, door_targets, player)

    elif world.shuffle[player] == 'restricted':
        simple_shuffle_dungeons(world, player)

        lw_entrances = list(Inverted_LW_Entrances + Inverted_LW_Single_Cave_Doors)
        dw_entrances = list(Inverted_DW_Entrances + Inverted_DW_Single_Cave_Doors + Inverted_Old_Man_Entrances)
        lw_must_exits = list(Inverted_LW_Entrances_Must_Exit)
        old_man_entrances = list(Inverted_Old_Man_Entrances)
        caves = list(Cave_Exits + Cave_Three_Exits + Old_Man_House)
        single_doors = list(Single_Cave_Doors)
        bomb_shop_doors = list(Inverted_Bomb_Shop_Single_Cave_Doors + Inverted_Bomb_Shop_Multi_Cave_Doors)
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors + Inverted_Blacksmith_Multi_Cave_Doors)
        door_targets = list(Inverted_Single_Cave_Targets)

        # place links house
        links_house_doors = [i for i in lw_entrances + dw_entrances + lw_must_exits if
                             i not in Inverted_Dark_Sanctuary_Doors + Isolated_LH_Doors]
        links_house = world.random.choice(list(links_house_doors))
        connect_two_way(world, links_house, 'Inverted Links House Exit', player)
        if links_house in lw_entrances:
            lw_entrances.remove(links_house)
        elif links_house in dw_entrances:
            dw_entrances.remove(links_house)
        elif links_house in lw_must_exits:
            lw_must_exits.remove(links_house)

        # place dark sanc
        sanc_doors = [door for door in Inverted_Dark_Sanctuary_Doors if door in dw_entrances]
        sanc_door = world.random.choice(sanc_doors)
        dw_entrances.remove(sanc_door)
        connect_entrance(world, sanc_door, 'Inverted Dark Sanctuary', player)
        world.get_entrance('Inverted Dark Sanctuary Exit', player).connect(
            world.get_entrance(sanc_door, player).parent_region)

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        # place must exits
        connect_mandatory_exits(world, lw_entrances, caves, lw_must_exits, player)

        # place old man, has limited options
        # exit has to come from specific set of doors, the entrance is free to move about
        old_man_entrances = [door for door in old_man_entrances if door in dw_entrances]
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        connect_two_way(world, old_man_exit, 'Old Man Cave Exit (East)', player)
        dw_entrances.remove(old_man_exit)

        # place blacksmith, has limited options
        all_entrances = lw_entrances + dw_entrances
        # cannot place it anywhere already taken (or that are otherwise not eligible for placement)
        blacksmith_doors = [door for door in blacksmith_doors if door in all_entrances]
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        if blacksmith_hut in lw_entrances:
            lw_entrances.remove(blacksmith_hut)
        if blacksmith_hut in dw_entrances:
            dw_entrances.remove(blacksmith_hut)
        bomb_shop_doors.extend(blacksmith_doors)

        # place bomb shop, has limited options
        all_entrances = lw_entrances + dw_entrances
        # cannot place it anywhere already taken (or that are otherwise not eligible for placement)
        bomb_shop_doors = [door for door in bomb_shop_doors if door in all_entrances]
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Inverted Big Bomb Shop', player)
        if bomb_shop in lw_entrances:
            lw_entrances.remove(bomb_shop)
        if bomb_shop in dw_entrances:
            dw_entrances.remove(bomb_shop)

        # place the old man cave's entrance somewhere in the dark world
        world.random.shuffle(dw_entrances)
        old_man_entrance = dw_entrances.pop()
        connect_two_way(world, old_man_entrance, 'Old Man Cave Exit (West)', player)

        # now scramble the rest
        connect_caves(world, lw_entrances, dw_entrances, caves, player)

        # scramble holes
        scramble_inverted_holes(world, player)

        doors = lw_entrances + dw_entrances
        # place remaining doors
        connect_doors(world, doors, door_targets, player)
    elif world.shuffle[player] == 'full':
        skull_woods_shuffle(world, player)

        lw_entrances = list(Inverted_LW_Entrances + Inverted_LW_Dungeon_Entrances + Inverted_LW_Single_Cave_Doors)
        dw_entrances = list(
            Inverted_DW_Entrances + Inverted_DW_Dungeon_Entrances + Inverted_DW_Single_Cave_Doors + Inverted_Old_Man_Entrances)
        lw_must_exits = list(Inverted_LW_Dungeon_Entrances_Must_Exit + Inverted_LW_Entrances_Must_Exit)
        old_man_entrances = list(
            Inverted_Old_Man_Entrances + Old_Man_Entrances + ['Inverted Agahnims Tower', 'Tower of Hera'])
        caves = list(
            Cave_Exits + Dungeon_Exits + Cave_Three_Exits)  # don't need to consider three exit caves, have one exit caves to avoid parity issues
        bomb_shop_doors = list(Inverted_Bomb_Shop_Single_Cave_Doors + Inverted_Bomb_Shop_Multi_Cave_Doors)
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors + Inverted_Blacksmith_Multi_Cave_Doors)
        door_targets = list(Inverted_Single_Cave_Targets)
        old_man_house = list(Old_Man_House)

        # randomize which desert ledge door is a must-exit
        if world.random.randint(0, 1) == 0:
            lw_must_exits.append('Desert Palace Entrance (North)')
            lw_entrances.append('Desert Palace Entrance (West)')
        else:
            lw_must_exits.append('Desert Palace Entrance (West)')
            lw_entrances.append('Desert Palace Entrance (North)')

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        lw_entrances.append('Hyrule Castle Entrance (South)')

        if not world.shuffle_ganon:
            connect_two_way(world, 'Inverted Ganons Tower', 'Inverted Ganons Tower Exit', player)
            hc_ledge_entrances = ['Hyrule Castle Entrance (West)', 'Hyrule Castle Entrance (East)']
        else:
            lw_entrances.append('Inverted Ganons Tower')
            caves.append('Inverted Ganons Tower Exit')
            hc_ledge_entrances = ['Hyrule Castle Entrance (West)', 'Hyrule Castle Entrance (East)',
                                  'Inverted Ganons Tower']

        # shuffle aga door first. if it's on hc ledge, then one other hc ledge door has to be must_exit
        all_entrances_aga = lw_entrances + dw_entrances
        aga_doors = [i for i in all_entrances_aga]
        world.random.shuffle(aga_doors)
        aga_door = aga_doors.pop()

        if aga_door in hc_ledge_entrances:
            lw_entrances.remove(aga_door)
            hc_ledge_entrances.remove(aga_door)

            world.random.shuffle(hc_ledge_entrances)
            hc_ledge_must_exit = hc_ledge_entrances.pop()
            lw_entrances.remove(hc_ledge_must_exit)
            lw_must_exits.append(hc_ledge_must_exit)
        elif aga_door in lw_entrances:
            lw_entrances.remove(aga_door)
        else:
            dw_entrances.remove(aga_door)

        connect_two_way(world, aga_door, 'Inverted Agahnims Tower Exit', player)
        caves.remove('Inverted Agahnims Tower Exit')

        # place links house
        links_house_doors = [i for i in lw_entrances + dw_entrances + lw_must_exits if
                             i not in Inverted_Dark_Sanctuary_Doors + Isolated_LH_Doors]
        links_house = world.random.choice(list(links_house_doors))
        connect_two_way(world, links_house, 'Inverted Links House Exit', player)
        if links_house in lw_entrances:
            lw_entrances.remove(links_house)
        if links_house in dw_entrances:
            dw_entrances.remove(links_house)
        if links_house in lw_must_exits:
            lw_must_exits.remove(links_house)

        # place dark sanc
        sanc_doors = [door for door in Inverted_Dark_Sanctuary_Doors if door in dw_entrances]
        sanc_door = world.random.choice(sanc_doors)
        dw_entrances.remove(sanc_door)
        connect_entrance(world, sanc_door, 'Inverted Dark Sanctuary', player)
        world.get_entrance('Inverted Dark Sanctuary Exit', player).connect(
            world.get_entrance(sanc_door, player).parent_region)

        # place old man house
        # no dw must exits in inverted, but we randomize whether cave is in light or dark world
        if world.random.randint(0, 1) == 0:
            caves += old_man_house
            connect_mandatory_exits(world, lw_entrances, caves, lw_must_exits, player)
            try:
                caves.remove(old_man_house[0])
            except ValueError:
                pass
            else:  # if the cave wasn't placed we get here
                connect_caves(world, lw_entrances, [], old_man_house, player)
        else:
            connect_caves(world, dw_entrances, [], old_man_house, player)
            connect_mandatory_exits(world, lw_entrances, caves, lw_must_exits, player)

        # put all HC exits in LW in inverted full shuffle
        connect_caves(world, lw_entrances, [],
                      [('Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)', 'Hyrule Castle Exit (South)')],
                      player)

        # place old man, has limited options
        # exit has to come from specific set of doors, the entrance is free to move about
        old_man_entrances = [door for door in old_man_entrances if door in dw_entrances + lw_entrances]
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        connect_two_way(world, old_man_exit, 'Old Man Cave Exit (East)', player)
        if old_man_exit in dw_entrances:
            dw_entrances.remove(old_man_exit)
            old_man_world = 'dark'
        elif old_man_exit in lw_entrances:
            lw_entrances.remove(old_man_exit)
            old_man_world = 'light'

        # place blacksmith, has limited options
        all_entrances = lw_entrances + dw_entrances
        # cannot place it anywhere already taken (or that are otherwise not eligible for placement)
        blacksmith_doors = [door for door in blacksmith_doors if door in all_entrances]
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        if blacksmith_hut in lw_entrances:
            lw_entrances.remove(blacksmith_hut)
        if blacksmith_hut in dw_entrances:
            dw_entrances.remove(blacksmith_hut)
        bomb_shop_doors.extend(blacksmith_doors)

        # place bomb shop, has limited options
        all_entrances = lw_entrances + dw_entrances
        # cannot place it anywhere already taken (or that are otherwise not eligible for placement)
        bomb_shop_doors = [door for door in bomb_shop_doors if door in all_entrances]
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Inverted Big Bomb Shop', player)
        if bomb_shop in lw_entrances:
            lw_entrances.remove(bomb_shop)
        if bomb_shop in dw_entrances:
            dw_entrances.remove(bomb_shop)

        # place the old man cave's entrance somewhere in the same world he'll exit from
        if old_man_world == 'light':
            world.random.shuffle(lw_entrances)
            old_man_entrance = lw_entrances.pop()
            connect_two_way(world, old_man_entrance, 'Old Man Cave Exit (West)', player)
        elif old_man_world == 'dark':
            world.random.shuffle(dw_entrances)
            old_man_entrance = dw_entrances.pop()
            connect_two_way(world, old_man_entrance, 'Old Man Cave Exit (West)', player)

        # now scramble the rest
        connect_caves(world, lw_entrances, dw_entrances, caves, player)

        # scramble holes
        scramble_inverted_holes(world, player)

        doors = lw_entrances + dw_entrances

        # place remaining doors
        connect_doors(world, doors, door_targets, player)
    elif world.shuffle[player] == 'crossed':
        skull_woods_shuffle(world, player)

        entrances = list(
            Inverted_LW_Entrances + Inverted_LW_Dungeon_Entrances + Inverted_LW_Single_Cave_Doors + Inverted_Old_Man_Entrances + Inverted_DW_Entrances + Inverted_DW_Dungeon_Entrances + Inverted_DW_Single_Cave_Doors)
        must_exits = list(Inverted_LW_Entrances_Must_Exit + Inverted_LW_Dungeon_Entrances_Must_Exit)

        old_man_entrances = list(
            Inverted_Old_Man_Entrances + Old_Man_Entrances + ['Inverted Agahnims Tower', 'Tower of Hera'])
        caves = list(
            Cave_Exits + Dungeon_Exits + Cave_Three_Exits + Old_Man_House)  # don't need to consider three exit caves, have one exit caves to avoid parity issues
        bomb_shop_doors = list(Inverted_Bomb_Shop_Single_Cave_Doors + Inverted_Bomb_Shop_Multi_Cave_Doors)
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors + Inverted_Blacksmith_Multi_Cave_Doors)
        door_targets = list(Inverted_Single_Cave_Targets)

        # randomize which desert ledge door is a must-exit
        if world.random.randint(0, 1) == 0:
            must_exits.append('Desert Palace Entrance (North)')
            entrances.append('Desert Palace Entrance (West)')
        else:
            must_exits.append('Desert Palace Entrance (West)')
            entrances.append('Desert Palace Entrance (North)')

        caves.append(tuple(world.random.sample(
            ['Hyrule Castle Exit (South)', 'Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'], 3)))
        entrances.append('Hyrule Castle Entrance (South)')

        if not world.shuffle_ganon:
            connect_two_way(world, 'Inverted Ganons Tower', 'Inverted Ganons Tower Exit', player)
            hc_ledge_entrances = ['Hyrule Castle Entrance (West)', 'Hyrule Castle Entrance (East)']
        else:
            entrances.append('Inverted Ganons Tower')
            caves.append('Inverted Ganons Tower Exit')
            hc_ledge_entrances = ['Hyrule Castle Entrance (West)', 'Hyrule Castle Entrance (East)',
                                  'Inverted Ganons Tower']

        # shuffle aga door. if it's on hc ledge, then one other hc ledge door has to be must_exit
        aga_door = world.random.choice(list(entrances))

        if aga_door in hc_ledge_entrances:
            hc_ledge_entrances.remove(aga_door)

            world.random.shuffle(hc_ledge_entrances)
            hc_ledge_must_exit = hc_ledge_entrances.pop()
            entrances.remove(hc_ledge_must_exit)
            must_exits.append(hc_ledge_must_exit)

        entrances.remove(aga_door)
        connect_two_way(world, aga_door, 'Inverted Agahnims Tower Exit', player)
        caves.remove('Inverted Agahnims Tower Exit')

        # place links house
        links_house_doors = [i for i in entrances + must_exits if
                             i not in Inverted_Dark_Sanctuary_Doors + Isolated_LH_Doors]
        links_house = world.random.choice(list(links_house_doors))
        connect_two_way(world, links_house, 'Inverted Links House Exit', player)
        if links_house in entrances:
            entrances.remove(links_house)
        elif links_house in must_exits:
            must_exits.remove(links_house)

        # place dark sanc
        sanc_doors = [door for door in Inverted_Dark_Sanctuary_Doors if door in entrances]
        sanc_door = world.random.choice(sanc_doors)
        entrances.remove(sanc_door)
        connect_entrance(world, sanc_door, 'Inverted Dark Sanctuary', player)
        world.get_entrance('Inverted Dark Sanctuary Exit', player).connect(
            world.get_entrance(sanc_door, player).parent_region)

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        # place must-exit caves
        connect_mandatory_exits(world, entrances, caves, must_exits, player)

        # place old man, has limited options
        # exit has to come from specific set of doors, the entrance is free to move about
        old_man_entrances = [door for door in old_man_entrances if door in entrances]
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        connect_two_way(world, old_man_exit, 'Old Man Cave Exit (East)', player)
        entrances.remove(old_man_exit)

        # place blacksmith, has limited options
        # cannot place it anywhere already taken (or that are otherwise not eligible for placement)
        blacksmith_doors = [door for door in blacksmith_doors if door in entrances]
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        entrances.remove(blacksmith_hut)

        # place bomb shop, has limited options

        # cannot place it anywhere already taken (or that are otherwise not eligible for placement)
        bomb_shop_doors = [door for door in bomb_shop_doors if door in entrances]
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Inverted Big Bomb Shop', player)
        entrances.remove(bomb_shop)

        # place the old man cave's entrance somewhere
        world.random.shuffle(entrances)
        old_man_entrance = entrances.pop()
        connect_two_way(world, old_man_entrance, 'Old Man Cave Exit (West)', player)

        # now scramble the rest
        connect_caves(world, entrances, [], caves, player)

        # scramble holes
        scramble_inverted_holes(world, player)

        # place remaining doors
        connect_doors(world, entrances, door_targets, player)
    elif world.shuffle[player] == 'insanity':
        # beware ye who enter here

        entrances = Inverted_LW_Entrances + Inverted_LW_Dungeon_Entrances + Inverted_DW_Entrances + Inverted_DW_Dungeon_Entrances + Inverted_Old_Man_Entrances + Old_Man_Entrances + [
            'Skull Woods Second Section Door (East)', 'Skull Woods Second Section Door (West)',
            'Skull Woods First Section Door', 'Kakariko Well Cave', 'Bat Cave Cave', 'North Fairy Cave', 'Sanctuary',
            'Lost Woods Hideout Stump', 'Lumberjack Tree Cave', 'Hyrule Castle Entrance (South)']
        entrances_must_exits = Inverted_LW_Entrances_Must_Exit + Inverted_LW_Dungeon_Entrances_Must_Exit

        doors = Inverted_LW_Entrances + Inverted_LW_Dungeon_Entrances + Inverted_LW_Entrances_Must_Exit + Inverted_LW_Dungeon_Entrances_Must_Exit + [
            'Kakariko Well Cave', 'Bat Cave Cave', 'North Fairy Cave', 'Sanctuary', 'Lost Woods Hideout Stump',
            'Lumberjack Tree Cave', 'Hyrule Castle Secret Entrance Stairs'] + Inverted_Old_Man_Entrances + \
                Inverted_DW_Entrances + Inverted_DW_Dungeon_Entrances + ['Skull Woods First Section Door',
                                                                         'Skull Woods Second Section Door (East)',
                                                                         'Skull Woods Second Section Door (West)'] + \
                Inverted_LW_Single_Cave_Doors + Inverted_DW_Single_Cave_Doors + ['Desert Palace Entrance (West)',
                                                                                 'Desert Palace Entrance (North)']

        # randomize which desert ledge door is a must-exit
        if world.random.randint(0, 1) == 0:
            entrances_must_exits.append('Desert Palace Entrance (North)')
            entrances.append('Desert Palace Entrance (West)')
        else:
            entrances_must_exits.append('Desert Palace Entrance (West)')
            entrances.append('Desert Palace Entrance (North)')

        # TODO: there are other possible entrances we could support here by way of exiting from a connector,
        # and rentering to find bomb shop. However appended list here is all those that we currently have
        # bomb shop logic for.
        # Specifically we could potentially add: 'Dark Death Mountain Ledge (East)' and doors associated with pits
        bomb_shop_doors = list(Inverted_Bomb_Shop_Single_Cave_Doors + Inverted_Bomb_Shop_Multi_Cave_Doors + [
            'Turtle Rock Isolated Ledge Entrance', 'Hookshot Cave Back Entrance'])
        blacksmith_doors = list(Blacksmith_Single_Cave_Doors + Inverted_Blacksmith_Multi_Cave_Doors)
        door_targets = list(Inverted_Single_Cave_Targets)

        world.random.shuffle(doors)

        old_man_entrances = list(Inverted_Old_Man_Entrances + Old_Man_Entrances) + ['Tower of Hera',
                                                                                    'Inverted Agahnims Tower']

        caves = Cave_Exits + Dungeon_Exits + Cave_Three_Exits + ['Old Man House Exit (Bottom)',
                                                                 'Old Man House Exit (Top)',
                                                                 'Skull Woods First Section Exit',
                                                                 'Skull Woods Second Section Exit (East)',
                                                                 'Skull Woods Second Section Exit (West)',
                                                                 'Kakariko Well Exit', 'Bat Cave Exit',
                                                                 'North Fairy Cave Exit', 'Lost Woods Hideout Exit',
                                                                 'Lumberjack Tree Exit', 'Sanctuary Exit']

        # shuffle up holes
        hole_entrances = ['Kakariko Well Drop', 'Bat Cave Drop', 'North Fairy Cave Drop', 'Lost Woods Hideout Drop',
                          'Lumberjack Tree Tree', 'Sanctuary Grave',
                          'Skull Woods First Section Hole (East)', 'Skull Woods First Section Hole (West)',
                          'Skull Woods First Section Hole (North)', 'Skull Woods Second Section Hole']

        hole_targets = ['Kakariko Well (top)', 'Bat Cave (right)', 'North Fairy Cave', 'Lost Woods Hideout (top)',
                        'Lumberjack Tree (top)', 'Sewer Drop', 'Skull Woods Second Section (Drop)',
                        'Skull Woods First Section (Left)', 'Skull Woods First Section (Right)',
                        'Skull Woods First Section (Top)']

        # tavern back door cannot be shuffled yet
        connect_doors(world, ['Tavern North'], ['Tavern'], player)

        hole_entrances.append('Hyrule Castle Secret Entrance Drop')
        hole_targets.append('Hyrule Castle Secret Entrance')
        entrances.append('Hyrule Castle Secret Entrance Stairs')
        caves.append('Hyrule Castle Secret Entrance Exit')

        if not world.shuffle_ganon:
            connect_two_way(world, 'Inverted Ganons Tower', 'Inverted Ganons Tower Exit', player)
            connect_two_way(world, 'Inverted Pyramid Entrance', 'Pyramid Exit', player)
            connect_entrance(world, 'Inverted Pyramid Hole', 'Pyramid', player)
        else:
            entrances.append('Inverted Ganons Tower')
            caves.extend(['Inverted Ganons Tower Exit', 'Pyramid Exit'])
            hole_entrances.append('Inverted Pyramid Hole')
            hole_targets.append('Pyramid')
            doors.extend(['Inverted Ganons Tower', 'Inverted Pyramid Entrance'])

        world.random.shuffle(hole_entrances)
        world.random.shuffle(hole_targets)
        world.random.shuffle(entrances)

        # fill up holes
        for hole in hole_entrances:
            connect_entrance(world, hole, hole_targets.pop(), player)

        doors.append('Hyrule Castle Entrance (South)')
        caves.append(('Hyrule Castle Exit (South)', 'Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'))

        # place links house and dark sanc
        links_house_doors = [i for i in entrances + entrances_must_exits if
                             i not in Inverted_Dark_Sanctuary_Doors + Isolated_LH_Doors]
        links_house = world.random.choice(list(links_house_doors))
        connect_two_way(world, links_house, 'Inverted Links House Exit', player)
        if links_house in entrances:
            entrances.remove(links_house)
        elif links_house in entrances_must_exits:
            entrances_must_exits.remove(links_house)
        doors.remove(links_house)

        sanc_doors = [door for door in Inverted_Dark_Sanctuary_Doors if door in entrances]
        sanc_door = world.random.choice(sanc_doors)
        entrances.remove(sanc_door)
        doors.remove(sanc_door)
        connect_entrance(world, sanc_door, 'Inverted Dark Sanctuary', player)
        world.get_entrance('Inverted Dark Sanctuary Exit', player).connect(
            world.get_entrance(sanc_door, player).parent_region)

        # now let's deal with mandatory reachable stuff
        def extract_reachable_exit(cavelist):
            world.random.shuffle(cavelist)
            candidate = None
            for cave in cavelist:
                if isinstance(cave, tuple) and len(cave) > 1:
                    # special handling: TRock has two entries that we should consider entrance only
                    # ToDo this should be handled in a more sensible manner
                    if cave[0] in ['Turtle Rock Exit (Front)', 'Spectacle Rock Cave Exit (Peak)'] and len(cave) == 2:
                        continue
                    candidate = cave
                    break
            if candidate is None:
                raise KeyError('No suitable cave.')
            cavelist.remove(candidate)
            return candidate

        def connect_reachable_exit(entrance, caves, doors):
            cave = extract_reachable_exit(caves)

            exit = cave[-1]
            cave = cave[:-1]
            connect_exit(world, exit, entrance, player)
            connect_entrance(world, doors.pop(), exit, player)
            # rest of cave now is forced to be in this world
            caves.append(cave)

        # connect mandatory exits
        for entrance in entrances_must_exits:
            connect_reachable_exit(entrance, caves, doors)

        # place old man, has limited options
        # exit has to come from specific set of doors, the entrance is free to move about
        old_man_entrances = [entrance for entrance in old_man_entrances if entrance in entrances]
        world.random.shuffle(old_man_entrances)
        old_man_exit = old_man_entrances.pop()
        entrances.remove(old_man_exit)

        connect_exit(world, 'Old Man Cave Exit (East)', old_man_exit, player)
        connect_entrance(world, doors.pop(), 'Old Man Cave Exit (East)', player)
        caves.append('Old Man Cave Exit (West)')

        # place blacksmith, has limited options
        blacksmith_doors = [door for door in blacksmith_doors if door in doors]
        world.random.shuffle(blacksmith_doors)
        blacksmith_hut = blacksmith_doors.pop()
        connect_entrance(world, blacksmith_hut, 'Blacksmiths Hut', player)
        doors.remove(blacksmith_hut)

        # place dam and pyramid fairy, have limited options
        bomb_shop_doors = [door for door in bomb_shop_doors if door in doors]
        world.random.shuffle(bomb_shop_doors)
        bomb_shop = bomb_shop_doors.pop()
        connect_entrance(world, bomb_shop, 'Inverted Big Bomb Shop', player)
        doors.remove(bomb_shop)

        # handle remaining caves
        for cave in caves:
            if isinstance(cave, str):
                cave = (cave,)

            for exit in cave:
                connect_exit(world, exit, entrances.pop(), player)
                connect_entrance(world, doors.pop(), exit, player)

        # place remaining doors
        connect_doors(world, doors, door_targets, player)
    else:
        raise NotImplementedError('Shuffling not supported yet')

    if world.logic[player] in ['owglitches', 'hybridglitches', 'nologic']:
        overworld_glitch_connections(world, player)
        # mandatory hybrid major glitches connections
        if world.logic[player] in ['hybridglitches', 'nologic']:
            underworld_glitch_connections(world, player)

    # patch swamp drain
    if world.get_entrance('Dam', player).connected_region.name != 'Dam' or world.get_entrance('Swamp Palace',
                                                                                              player).connected_region.name != 'Swamp Palace (Entrance)':
        world.swamp_patch_required[player] = True

    # check for potion shop location
    if world.get_entrance('Potion Shop', player).connected_region.name != 'Potion Shop':
        world.powder_patch_required[player] = True

    # check for ganon location
    if world.get_entrance('Inverted Pyramid Hole', player).connected_region.name != 'Pyramid':
        world.ganon_at_pyramid[player] = False

    # check for Ganon's Tower location
    if world.get_entrance('Inverted Ganons Tower', player).connected_region.name != 'Ganons Tower (Entrance)':
        world.ganonstower_vanilla[player] = False


def connect_simple(world, exitname, regionname, player):
    world.get_entrance(exitname, player).connect(world.get_region(regionname, player))


def connect_entrance(world, entrancename: str, exitname: str, player: int):
    entrance = world.get_entrance(entrancename, player)
    # check if we got an entrance or a region to connect to
    try:
        region = world.get_region(exitname, player)
        exit = None
    except KeyError:
        exit = world.get_entrance(exitname, player)
        region = exit.parent_region

    # if this was already connected somewhere, remove the backreference
    if entrance.connected_region is not None:
        entrance.connected_region.entrances.remove(entrance)

    target = exit_ids[exit.name][0] if exit is not None else exit_ids.get(region.name, None)
    addresses = door_addresses[entrance.name][0]

    entrance.connect(region, addresses, target)
    world.spoiler.set_entrance(entrance.name, exit.name if exit is not None else region.name, 'entrance', player)


def connect_exit(world, exitname, entrancename, player):
    entrance = world.get_entrance(entrancename, player)
    exit = world.get_entrance(exitname, player)

    # if this was already connected somewhere, remove the backreference
    if exit.connected_region is not None:
        exit.connected_region.entrances.remove(exit)

    exit.connect(entrance.parent_region, door_addresses[entrance.name][1], exit_ids[exit.name][1])
    world.spoiler.set_entrance(entrance.name, exit.name, 'exit', player)


def connect_two_way(world, entrancename, exitname, player):
    entrance = world.get_entrance(entrancename, player)
    exit = world.get_entrance(exitname, player)

    # if these were already connected somewhere, remove the backreference
    if entrance.connected_region is not None:
        entrance.connected_region.entrances.remove(entrance)
    if exit.connected_region is not None:
        exit.connected_region.entrances.remove(exit)

    entrance.connect(exit.parent_region, door_addresses[entrance.name][0], exit_ids[exit.name][0])
    exit.connect(entrance.parent_region, door_addresses[entrance.name][1], exit_ids[exit.name][1])
    world.spoiler.set_entrance(entrance.name, exit.name, 'both', player)


def scramble_holes(world, player):
    hole_entrances = [('Kakariko Well Cave', 'Kakariko Well Drop'),
                      ('Bat Cave Cave', 'Bat Cave Drop'),
                      ('North Fairy Cave', 'North Fairy Cave Drop'),
                      ('Lost Woods Hideout Stump', 'Lost Woods Hideout Drop'),
                      ('Lumberjack Tree Cave', 'Lumberjack Tree Tree'),
                      ('Sanctuary', 'Sanctuary Grave')]

    hole_targets = [('Kakariko Well Exit', 'Kakariko Well (top)'),
                    ('Bat Cave Exit', 'Bat Cave (right)'),
                    ('North Fairy Cave Exit', 'North Fairy Cave'),
                    ('Lost Woods Hideout Exit', 'Lost Woods Hideout (top)'),
                    ('Lumberjack Tree Exit', 'Lumberjack Tree (top)')]

    if not world.shuffle_ganon:
        connect_two_way(world, 'Pyramid Entrance', 'Pyramid Exit', player)
        connect_entrance(world, 'Pyramid Hole', 'Pyramid', player)
    else:
        hole_targets.append(('Pyramid Exit', 'Pyramid'))

    if world.mode[player] == 'standard':
        # cannot move uncle cave
        connect_two_way(world, 'Hyrule Castle Secret Entrance Stairs', 'Hyrule Castle Secret Entrance Exit', player)
        connect_entrance(world, 'Hyrule Castle Secret Entrance Drop', 'Hyrule Castle Secret Entrance', player)
    else:
        hole_entrances.append(('Hyrule Castle Secret Entrance Stairs', 'Hyrule Castle Secret Entrance Drop'))
        hole_targets.append(('Hyrule Castle Secret Entrance Exit', 'Hyrule Castle Secret Entrance'))

    # do not shuffle sanctuary into pyramid hole unless shuffle is crossed
    if world.shuffle[player] == 'crossed':
        hole_targets.append(('Sanctuary Exit', 'Sewer Drop'))
    if world.shuffle_ganon:
        world.random.shuffle(hole_targets)
        exit, target = hole_targets.pop()
        connect_two_way(world, 'Pyramid Entrance', exit, player)
        connect_entrance(world, 'Pyramid Hole', target, player)
    if world.shuffle[player] != 'crossed':
        hole_targets.append(('Sanctuary Exit', 'Sewer Drop'))

    world.random.shuffle(hole_targets)
    for entrance, drop in hole_entrances:
        exit, target = hole_targets.pop()
        connect_two_way(world, entrance, exit, player)
        connect_entrance(world, drop, target, player)


def scramble_inverted_holes(world, player):
    hole_entrances = [('Kakariko Well Cave', 'Kakariko Well Drop'),
                      ('Bat Cave Cave', 'Bat Cave Drop'),
                      ('North Fairy Cave', 'North Fairy Cave Drop'),
                      ('Lost Woods Hideout Stump', 'Lost Woods Hideout Drop'),
                      ('Lumberjack Tree Cave', 'Lumberjack Tree Tree'),
                      ('Sanctuary', 'Sanctuary Grave')]

    hole_targets = [('Kakariko Well Exit', 'Kakariko Well (top)'),
                    ('Bat Cave Exit', 'Bat Cave (right)'),
                    ('North Fairy Cave Exit', 'North Fairy Cave'),
                    ('Lost Woods Hideout Exit', 'Lost Woods Hideout (top)'),
                    ('Lumberjack Tree Exit', 'Lumberjack Tree (top)')]

    if not world.shuffle_ganon:
        connect_two_way(world, 'Inverted Pyramid Entrance', 'Pyramid Exit', player)
        connect_entrance(world, 'Inverted Pyramid Hole', 'Pyramid', player)
    else:
        hole_targets.append(('Pyramid Exit', 'Pyramid'))

    hole_entrances.append(('Hyrule Castle Secret Entrance Stairs', 'Hyrule Castle Secret Entrance Drop'))
    hole_targets.append(('Hyrule Castle Secret Entrance Exit', 'Hyrule Castle Secret Entrance'))

    # do not shuffle sanctuary into pyramid hole unless shuffle is crossed
    if world.shuffle[player] == 'crossed':
        hole_targets.append(('Sanctuary Exit', 'Sewer Drop'))
    if world.shuffle_ganon:
        world.random.shuffle(hole_targets)
        exit, target = hole_targets.pop()
        connect_two_way(world, 'Inverted Pyramid Entrance', exit, player)
        connect_entrance(world, 'Inverted Pyramid Hole', target, player)
    if world.shuffle[player] != 'crossed':
        hole_targets.append(('Sanctuary Exit', 'Sewer Drop'))

    world.random.shuffle(hole_targets)
    for entrance, drop in hole_entrances:
        exit, target = hole_targets.pop()
        connect_two_way(world, entrance, exit, player)
        connect_entrance(world, drop, target, player)


def connect_random(world, exitlist, targetlist, player, two_way=False):
    targetlist = list(targetlist)
    world.random.shuffle(targetlist)

    for exit, target in zip(exitlist, targetlist):
        if two_way:
            connect_two_way(world, exit, target, player)
        else:
            connect_entrance(world, exit, target, player)


def connect_mandatory_exits(world, entrances, caves, must_be_exits, player):
    # Keeps track of entrances that cannot be used to access each exit / cave
    if world.mode[player] == 'inverted':
        invalid_connections = Inverted_Must_Exit_Invalid_Connections.copy()
    else:
        invalid_connections = Must_Exit_Invalid_Connections.copy()
    invalid_cave_connections = defaultdict(set)

    if world.logic[player] in ['owglitches', 'hybridglitches', 'nologic']:
        from worlds.alttp import OverworldGlitchRules
        for entrance in OverworldGlitchRules.get_non_mandatory_exits(world.mode[player] == 'inverted'):
            invalid_connections[entrance] = set()
            if entrance in must_be_exits:
                must_be_exits.remove(entrance)
                entrances.append(entrance)

    """This works inplace"""
    world.random.shuffle(entrances)
    world.random.shuffle(caves)

    # Handle inverted Aga Tower - if it depends on connections, then so does Hyrule Castle Ledge
    if world.mode[player] == 'inverted':
        for entrance in invalid_connections:
            if world.get_entrance(entrance, player).connected_region == world.get_region('Inverted Agahnims Tower',
                                                                                         player):
                for exit in invalid_connections[entrance]:
                    invalid_connections[exit] = invalid_connections[exit].union(
                        {'Inverted Ganons Tower', 'Hyrule Castle Entrance (West)', 'Hyrule Castle Entrance (East)'})
                break

    used_caves = []
    required_entrances = 0  # Number of entrances reserved for used_caves
    while must_be_exits:
        exit = must_be_exits.pop()
        # find multi exit cave
        cave = None
        for candidate in caves:
            if not isinstance(candidate, str) and (
                    candidate in used_caves or len(candidate) < len(entrances) - required_entrances - 1):
                cave = candidate
                break

        if cave is None:
            raise KeyError('No more caves left. Should not happen!')

        # all caves are sorted so that the last exit is always reachable
        connect_two_way(world, exit, cave[-1], player)
        if len(cave) == 2:
            entrance = next(e for e in entrances[::-1] if
                            e not in invalid_connections[exit] and e not in invalid_cave_connections[tuple(cave)])
            entrances.remove(entrance)
            connect_two_way(world, entrance, cave[0], player)
            if cave in used_caves:
                required_entrances -= 2
                used_caves.remove(cave)
            if entrance in invalid_connections:
                for exit2 in invalid_connections[entrance]:
                    invalid_connections[exit2] = invalid_connections[exit2].union(invalid_connections[exit]).union(
                        invalid_cave_connections[tuple(cave)])
        elif cave[-1] == 'Spectacle Rock Cave Exit':  # Spectacle rock only has one exit
            cave_entrances = []
            for cave_exit in cave[:-1]:
                entrance = next(e for e in entrances[::-1] if e not in invalid_connections[exit])
                cave_entrances.append(entrance)
                entrances.remove(entrance)
                connect_two_way(world, entrance, cave_exit, player)
                if entrance not in invalid_connections:
                    invalid_connections[exit] = set()
            if all(entrance in invalid_connections for entrance in cave_entrances):
                new_invalid_connections = invalid_connections[cave_entrances[0]].intersection(
                    invalid_connections[cave_entrances[1]])
                for exit2 in new_invalid_connections:
                    invalid_connections[exit2] = invalid_connections[exit2].union(invalid_connections[exit])
        else:  # save for later so we can connect to multiple exits
            if cave in used_caves:
                required_entrances -= 1
                used_caves.remove(cave)
            else:
                required_entrances += len(cave) - 1
            caves.append(cave[0:-1])
            world.random.shuffle(caves)
            used_caves.append(cave[0:-1])
            invalid_cave_connections[tuple(cave[0:-1])] = invalid_cave_connections[tuple(cave)].union(
                invalid_connections[exit])
        caves.remove(cave)
    for cave in used_caves:
        if cave in caves:  # check if we placed multiple entrances from this 3 or 4 exit
            for cave_exit in cave:
                entrance = next(e for e in entrances[::-1] if e not in invalid_cave_connections[tuple(cave)])
                invalid_cave_connections[tuple(cave)] = set()
                entrances.remove(entrance)
                connect_two_way(world, entrance, cave_exit, player)
            caves.remove(cave)


def connect_caves(world, lw_entrances, dw_entrances, caves, player):
    """This works inplace"""
    world.random.shuffle(lw_entrances)
    world.random.shuffle(dw_entrances)
    world.random.shuffle(caves)
    # connect highest exit count caves first, prevent issue where we have 2 or 3 exits accross worlds left to fill
    caves.sort(key=lambda cave: 1 if isinstance(cave, str) else len(cave), reverse=True)
    for cave in caves:
        target = lw_entrances if world.random.randint(0, 1) else dw_entrances
        if isinstance(cave, str):
            cave = (cave,)

        # check if we can still fit the cave into our target group
        if len(target) < len(cave):
            # need to use other set
            target = lw_entrances if target is dw_entrances else dw_entrances

        for exit in cave:
            connect_two_way(world, target.pop(), exit, player)
    caves.clear()  # emulating old behaviour of popping caves from the list in-place


def connect_doors(world, doors, targets, player):
    """This works inplace"""
    world.random.shuffle(doors)
    world.random.shuffle(targets)
    placing = min(len(doors), len(targets))
    for door, target in zip(doors, targets):
        connect_entrance(world, door, target, player)
    doors[:] = doors[placing:]
    targets[:] = targets[placing:]


def skull_woods_shuffle(world, player):
    connect_random(world, ['Skull Woods First Section Hole (East)', 'Skull Woods First Section Hole (West)',
                           'Skull Woods First Section Hole (North)', 'Skull Woods Second Section Hole'],
                   ['Skull Woods First Section (Left)', 'Skull Woods First Section (Right)',
                    'Skull Woods First Section (Top)', 'Skull Woods Second Section (Drop)'], player)
    connect_random(world, ['Skull Woods First Section Door', 'Skull Woods Second Section Door (East)',
                           'Skull Woods Second Section Door (West)'],
                   ['Skull Woods First Section Exit', 'Skull Woods Second Section Exit (East)',
                    'Skull Woods Second Section Exit (West)'], player, True)


def simple_shuffle_dungeons(world, player):
    skull_woods_shuffle(world, player)

    dungeon_entrances = ['Eastern Palace', 'Tower of Hera', 'Thieves Town', 'Skull Woods Final Section',
                         'Palace of Darkness', 'Ice Palace', 'Misery Mire', 'Swamp Palace']
    dungeon_exits = ['Eastern Palace Exit', 'Tower of Hera Exit', 'Thieves Town Exit', 'Skull Woods Final Section Exit',
                     'Palace of Darkness Exit', 'Ice Palace Exit', 'Misery Mire Exit', 'Swamp Palace Exit']

    if world.mode[player] != 'inverted':
        if not world.shuffle_ganon:
            connect_two_way(world, 'Ganons Tower', 'Ganons Tower Exit', player)
        else:
            dungeon_entrances.append('Ganons Tower')
            dungeon_exits.append('Ganons Tower Exit')
    else:
        dungeon_entrances.append('Inverted Agahnims Tower')
        dungeon_exits.append('Inverted Agahnims Tower Exit')

    # shuffle up single entrance dungeons
    connect_random(world, dungeon_entrances, dungeon_exits, player, True)

    # mix up 4 door dungeons
    multi_dungeons = ['Desert', 'Turtle Rock']
    if world.mode[player] == 'open' or (world.mode[player] == 'inverted' and world.shuffle_ganon):
        multi_dungeons.append('Hyrule Castle')
    world.random.shuffle(multi_dungeons)

    dp_target = multi_dungeons[0]
    tr_target = multi_dungeons[1]
    if world.mode[player] not in ['open', 'inverted'] or (
            world.mode[player] == 'inverted' and world.shuffle_ganon is False):
        # place hyrule castle as intended
        hc_target = 'Hyrule Castle'
    else:
        hc_target = multi_dungeons[2]

    # ToDo improve this?

    if world.mode[player] != 'inverted':
        if hc_target == 'Hyrule Castle':
            connect_two_way(world, 'Hyrule Castle Entrance (South)', 'Hyrule Castle Exit (South)', player)
            connect_two_way(world, 'Hyrule Castle Entrance (East)', 'Hyrule Castle Exit (East)', player)
            connect_two_way(world, 'Hyrule Castle Entrance (West)', 'Hyrule Castle Exit (West)', player)
            connect_two_way(world, 'Agahnims Tower', 'Agahnims Tower Exit', player)
        elif hc_target == 'Desert':
            connect_two_way(world, 'Desert Palace Entrance (South)', 'Hyrule Castle Exit (South)', player)
            connect_two_way(world, 'Desert Palace Entrance (East)', 'Hyrule Castle Exit (East)', player)
            connect_two_way(world, 'Desert Palace Entrance (West)', 'Hyrule Castle Exit (West)', player)
            connect_two_way(world, 'Desert Palace Entrance (North)', 'Agahnims Tower Exit', player)
        elif hc_target == 'Turtle Rock':
            connect_two_way(world, 'Turtle Rock', 'Hyrule Castle Exit (South)', player)
            connect_two_way(world, 'Turtle Rock Isolated Ledge Entrance', 'Hyrule Castle Exit (East)', player)
            connect_two_way(world, 'Dark Death Mountain Ledge (West)', 'Hyrule Castle Exit (West)', player)
            connect_two_way(world, 'Dark Death Mountain Ledge (East)', 'Agahnims Tower Exit', player)

        if dp_target == 'Hyrule Castle':
            connect_two_way(world, 'Hyrule Castle Entrance (South)', 'Desert Palace Exit (South)', player)
            connect_two_way(world, 'Hyrule Castle Entrance (East)', 'Desert Palace Exit (East)', player)
            connect_two_way(world, 'Hyrule Castle Entrance (West)', 'Desert Palace Exit (West)', player)
            connect_two_way(world, 'Agahnims Tower', 'Desert Palace Exit (North)', player)
        elif dp_target == 'Desert':
            connect_two_way(world, 'Desert Palace Entrance (South)', 'Desert Palace Exit (South)', player)
            connect_two_way(world, 'Desert Palace Entrance (East)', 'Desert Palace Exit (East)', player)
            connect_two_way(world, 'Desert Palace Entrance (West)', 'Desert Palace Exit (West)', player)
            connect_two_way(world, 'Desert Palace Entrance (North)', 'Desert Palace Exit (North)', player)
        elif dp_target == 'Turtle Rock':
            connect_two_way(world, 'Turtle Rock', 'Desert Palace Exit (South)', player)
            connect_two_way(world, 'Turtle Rock Isolated Ledge Entrance', 'Desert Palace Exit (East)', player)
            connect_two_way(world, 'Dark Death Mountain Ledge (West)', 'Desert Palace Exit (West)', player)
            connect_two_way(world, 'Dark Death Mountain Ledge (East)', 'Desert Palace Exit (North)', player)

        if tr_target == 'Hyrule Castle':
            connect_two_way(world, 'Hyrule Castle Entrance (South)', 'Turtle Rock Exit (Front)', player)
            connect_two_way(world, 'Hyrule Castle Entrance (East)', 'Turtle Rock Ledge Exit (East)', player)
            connect_two_way(world, 'Hyrule Castle Entrance (West)', 'Turtle Rock Ledge Exit (West)', player)
            connect_two_way(world, 'Agahnims Tower', 'Turtle Rock Isolated Ledge Exit', player)
        elif tr_target == 'Desert':
            connect_two_way(world, 'Desert Palace Entrance (South)', 'Turtle Rock Exit (Front)', player)
            connect_two_way(world, 'Desert Palace Entrance (North)', 'Turtle Rock Ledge Exit (East)', player)
            connect_two_way(world, 'Desert Palace Entrance (West)', 'Turtle Rock Ledge Exit (West)', player)
            connect_two_way(world, 'Desert Palace Entrance (East)', 'Turtle Rock Isolated Ledge Exit', player)
        elif tr_target == 'Turtle Rock':
            connect_two_way(world, 'Turtle Rock', 'Turtle Rock Exit (Front)', player)
            connect_two_way(world, 'Turtle Rock Isolated Ledge Entrance', 'Turtle Rock Isolated Ledge Exit', player)
            connect_two_way(world, 'Dark Death Mountain Ledge (West)', 'Turtle Rock Ledge Exit (West)', player)
            connect_two_way(world, 'Dark Death Mountain Ledge (East)', 'Turtle Rock Ledge Exit (East)', player)
    else:
        if hc_target == 'Hyrule Castle':
            connect_two_way(world, 'Hyrule Castle Entrance (South)', 'Hyrule Castle Exit (South)', player)
            connect_two_way(world, 'Hyrule Castle Entrance (East)', 'Hyrule Castle Exit (East)', player)
            connect_two_way(world, 'Hyrule Castle Entrance (West)', 'Hyrule Castle Exit (West)', player)
            connect_two_way(world, 'Inverted Ganons Tower', 'Inverted Ganons Tower Exit', player)
        elif hc_target == 'Desert':
            connect_two_way(world, 'Desert Palace Entrance (South)', 'Hyrule Castle Exit (South)', player)
            connect_two_way(world, 'Desert Palace Entrance (East)', 'Hyrule Castle Exit (East)', player)
            connect_two_way(world, 'Desert Palace Entrance (West)', 'Hyrule Castle Exit (West)', player)
            connect_two_way(world, 'Desert Palace Entrance (North)', 'Inverted Ganons Tower Exit', player)
        elif hc_target == 'Turtle Rock':
            connect_two_way(world, 'Turtle Rock', 'Hyrule Castle Exit (South)', player)
            connect_two_way(world, 'Turtle Rock Isolated Ledge Entrance', 'Inverted Ganons Tower Exit', player)
            connect_two_way(world, 'Dark Death Mountain Ledge (West)', 'Hyrule Castle Exit (West)', player)
            connect_two_way(world, 'Dark Death Mountain Ledge (East)', 'Hyrule Castle Exit (East)', player)

        if dp_target == 'Hyrule Castle':
            connect_two_way(world, 'Hyrule Castle Entrance (South)', 'Desert Palace Exit (South)', player)
            connect_two_way(world, 'Hyrule Castle Entrance (East)', 'Desert Palace Exit (East)', player)
            connect_two_way(world, 'Hyrule Castle Entrance (West)', 'Desert Palace Exit (West)', player)
            connect_two_way(world, 'Inverted Ganons Tower', 'Desert Palace Exit (North)', player)
        elif dp_target == 'Desert':
            connect_two_way(world, 'Desert Palace Entrance (South)', 'Desert Palace Exit (South)', player)
            connect_two_way(world, 'Desert Palace Entrance (East)', 'Desert Palace Exit (East)', player)
            connect_two_way(world, 'Desert Palace Entrance (West)', 'Desert Palace Exit (West)', player)
            connect_two_way(world, 'Desert Palace Entrance (North)', 'Desert Palace Exit (North)', player)
        elif dp_target == 'Turtle Rock':
            connect_two_way(world, 'Turtle Rock', 'Desert Palace Exit (South)', player)
            connect_two_way(world, 'Turtle Rock Isolated Ledge Entrance', 'Desert Palace Exit (East)', player)
            connect_two_way(world, 'Dark Death Mountain Ledge (West)', 'Desert Palace Exit (West)', player)
            connect_two_way(world, 'Dark Death Mountain Ledge (East)', 'Desert Palace Exit (North)', player)

        if tr_target == 'Hyrule Castle':
            connect_two_way(world, 'Hyrule Castle Entrance (South)', 'Turtle Rock Exit (Front)', player)
            connect_two_way(world, 'Hyrule Castle Entrance (East)', 'Turtle Rock Ledge Exit (East)', player)
            connect_two_way(world, 'Hyrule Castle Entrance (West)', 'Turtle Rock Ledge Exit (West)', player)
            connect_two_way(world, 'Inverted Ganons Tower', 'Turtle Rock Isolated Ledge Exit', player)
        elif tr_target == 'Desert':
            connect_two_way(world, 'Desert Palace Entrance (South)', 'Turtle Rock Exit (Front)', player)
            connect_two_way(world, 'Desert Palace Entrance (North)', 'Turtle Rock Ledge Exit (East)', player)
            connect_two_way(world, 'Desert Palace Entrance (West)', 'Turtle Rock Ledge Exit (West)', player)
            connect_two_way(world, 'Desert Palace Entrance (East)', 'Turtle Rock Isolated Ledge Exit', player)
        elif tr_target == 'Turtle Rock':
            connect_two_way(world, 'Turtle Rock', 'Turtle Rock Exit (Front)', player)
            connect_two_way(world, 'Turtle Rock Isolated Ledge Entrance', 'Turtle Rock Isolated Ledge Exit', player)
            connect_two_way(world, 'Dark Death Mountain Ledge (West)', 'Turtle Rock Ledge Exit (West)', player)
            connect_two_way(world, 'Dark Death Mountain Ledge (East)', 'Turtle Rock Ledge Exit (East)', player)


def crossed_shuffle_dungeons(world, player: int):
    lw_entrances = LW_Dungeon_Entrances.copy()
    dw_entrances = DW_Dungeon_Entrances.copy()

    for exitname, regionname in default_connections:
        connect_simple(world, exitname, regionname, player)

    skull_woods_shuffle(world, player)

    dungeon_exits = Dungeon_Exits_Base.copy()
    dungeon_entrances = lw_entrances + dw_entrances

    if not world.shuffle_ganon:
        connect_two_way(world, 'Ganons Tower', 'Ganons Tower Exit', player)
    else:
        dungeon_entrances.append('Ganons Tower')
        dungeon_exits.append('Ganons Tower Exit')

    if world.mode[player] == 'standard':
        # must connect front of hyrule castle to do escape
        connect_two_way(world, 'Hyrule Castle Entrance (South)', 'Hyrule Castle Exit (South)', player)
    else:
        dungeon_exits.append(('Hyrule Castle Exit (South)', 'Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'))
        dungeon_entrances.append('Hyrule Castle Entrance (South)')

    connect_mandatory_exits(world, dungeon_entrances, dungeon_exits,
                            LW_Dungeon_Entrances_Must_Exit + DW_Dungeon_Entrances_Must_Exit, player)

    if world.mode[player] == 'standard':
        connect_caves(world, dungeon_entrances, [], [('Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)')],
                      player)

    connect_caves(world, dungeon_entrances, [], dungeon_exits, player)
    assert not dungeon_exits  # make sure all exits are accounted for


def inverted_crossed_shuffle_dungeons(world, player: int):
    lw_entrances = Inverted_LW_Dungeon_Entrances.copy()
    dw_entrances = Inverted_DW_Dungeon_Entrances.copy()
    lw_dungeon_entrances_must_exit = list(Inverted_LW_Dungeon_Entrances_Must_Exit)
    for exitname, regionname in inverted_default_connections:
        connect_simple(world, exitname, regionname, player)

    skull_woods_shuffle(world, player)

    dungeon_exits = Inverted_Dungeon_Exits_Base.copy()
    dungeon_entrances = lw_entrances + dw_entrances

    # randomize which desert ledge door is a must-exit
    if world.random.randint(0, 1):
        lw_dungeon_entrances_must_exit.append('Desert Palace Entrance (North)')
        dungeon_entrances.append('Desert Palace Entrance (West)')
    else:
        lw_dungeon_entrances_must_exit.append('Desert Palace Entrance (West)')
        dungeon_entrances.append('Desert Palace Entrance (North)')

    dungeon_exits.append(('Hyrule Castle Exit (South)', 'Hyrule Castle Exit (West)', 'Hyrule Castle Exit (East)'))
    dungeon_entrances.append('Hyrule Castle Entrance (South)')

    if not world.shuffle_ganon:
        connect_two_way(world, 'Inverted Ganons Tower', 'Inverted Ganons Tower Exit', player)
        hc_ledge_entrances = ['Hyrule Castle Entrance (West)', 'Hyrule Castle Entrance (East)']
    else:
        dungeon_entrances.append('Inverted Ganons Tower')
        dungeon_exits.append('Inverted Ganons Tower Exit')
        hc_ledge_entrances = ['Hyrule Castle Entrance (West)', 'Hyrule Castle Entrance (East)', 'Inverted Ganons Tower']

    # shuffle aga door first. If it's on HC ledge, remaining HC ledge door must be must-exit
    world.random.shuffle(dungeon_entrances)
    aga_door = dungeon_entrances.pop()

    if aga_door in hc_ledge_entrances:
        hc_ledge_entrances.remove(aga_door)
        world.random.shuffle(hc_ledge_entrances)
        hc_ledge_must_exit = hc_ledge_entrances.pop()
        dungeon_entrances.remove(hc_ledge_must_exit)
        lw_dungeon_entrances_must_exit.append(hc_ledge_must_exit)

    connect_two_way(world, aga_door, 'Inverted Agahnims Tower Exit', player)
    dungeon_exits.remove('Inverted Agahnims Tower Exit')

    connect_mandatory_exits(world, dungeon_entrances, dungeon_exits, lw_dungeon_entrances_must_exit, player)

    connect_caves(world, dungeon_entrances, [], dungeon_exits, player)
    assert not dungeon_exits  # make sure all exits are accounted for


def unbias_some_entrances(world, Dungeon_Exits, Cave_Exits, Old_Man_House, Cave_Three_Exits):
    def shuffle_lists_in_list(ls):
        for i, item in enumerate(ls):
            if isinstance(item, list):
                ls[i] = world.random.sample(item, len(item))

    def tuplize_lists_in_list(ls):
        for i, item in enumerate(ls):
            if isinstance(item, list):
                ls[i] = tuple(item)

    shuffle_lists_in_list(Dungeon_Exits)
    shuffle_lists_in_list(Cave_Exits)
    shuffle_lists_in_list(Old_Man_House)
    shuffle_lists_in_list(Cave_Three_Exits)

    # paradox fixup
    if Cave_Three_Exits[1][0] == "Paradox Cave Exit (Bottom)":
        i = world.random.randint(1, 2)
        Cave_Three_Exits[1][0] = Cave_Three_Exits[1][i]
        Cave_Three_Exits[1][i] = "Paradox Cave Exit (Bottom)"

    # TR fixup
    tr_fixup = False
    for i, item in enumerate(Dungeon_Exits[-1]):
        if 'Turtle Rock Ledge Exit (East)' == item:
            tr_fixup = True
            if 0 != i:
                Dungeon_Exits[-1][i] = Dungeon_Exits[-1][0]
                Dungeon_Exits[-1][0] = 'Turtle Rock Ledge Exit (East)'
            break

    if not tr_fixup: raise RuntimeError("TR entrance shuffle fixup didn't happen")

    tuplize_lists_in_list(Dungeon_Exits)
    tuplize_lists_in_list(Cave_Exits)
    tuplize_lists_in_list(Old_Man_House)
    tuplize_lists_in_list(Cave_Three_Exits)


lookup = {
    "both": connect_two_way,
    "entrance": connect_entrance,
    "exit": lambda x, y, z, w: connect_exit(x, z, y, w)
}


def plando_connect(world, player: int):
    if world.plando_connections[player]:
        for connection in world.plando_connections[player]:
            func = lookup[connection.direction]
            try:
                func(world, connection.entrance, connection.exit, player)
            except Exception as e:
                raise Exception(f"Could not connect using {connection}") from e


LW_Dungeon_Entrances = ['Desert Palace Entrance (South)',
                        'Desert Palace Entrance (West)',
                        'Desert Palace Entrance (North)',
                        'Eastern Palace',
                        'Tower of Hera',
                        'Hyrule Castle Entrance (West)',
                        'Hyrule Castle Entrance (East)',
                        'Agahnims Tower']

LW_Dungeon_Entrances_Must_Exit = ['Desert Palace Entrance (East)']

DW_Dungeon_Entrances = ['Thieves Town',
                        'Skull Woods Final Section',
                        'Ice Palace',
                        'Misery Mire',
                        'Palace of Darkness',
                        'Swamp Palace',
                        'Turtle Rock',
                        'Dark Death Mountain Ledge (West)']

DW_Dungeon_Entrances_Must_Exit = ['Dark Death Mountain Ledge (East)',
                                  'Turtle Rock Isolated Ledge Entrance']

Dungeon_Exits_Base = [['Desert Palace Exit (South)', 'Desert Palace Exit (West)', 'Desert Palace Exit (East)'],
                      'Desert Palace Exit (North)',
                      'Eastern Palace Exit',
                      'Tower of Hera Exit',
                      'Thieves Town Exit',
                      'Skull Woods Final Section Exit',
                      'Ice Palace Exit',
                      'Misery Mire Exit',
                      'Palace of Darkness Exit',
                      'Swamp Palace Exit',
                      'Agahnims Tower Exit',
                      ['Turtle Rock Ledge Exit (East)',
                       'Turtle Rock Exit (Front)', 'Turtle Rock Ledge Exit (West)', 'Turtle Rock Isolated Ledge Exit']]

DW_Entrances_Must_Exit = ['Bumper Cave (Top)', 'Hookshot Cave Back Entrance']

Two_Door_Caves_Directional = [('Bumper Cave (Bottom)', 'Bumper Cave (Top)'),
                              ('Hookshot Cave', 'Hookshot Cave Back Entrance')]

Two_Door_Caves = [('Elder House (East)', 'Elder House (West)'),
                  ('Two Brothers House (East)', 'Two Brothers House (West)'),
                  ('Superbunny Cave (Bottom)', 'Superbunny Cave (Top)')]

Old_Man_Entrances = ['Old Man Cave (East)',
                     'Old Man House (Top)',
                     'Death Mountain Return Cave (East)',
                     'Spectacle Rock Cave',
                     'Spectacle Rock Cave Peak',
                     'Spectacle Rock Cave (Bottom)']

Old_Man_House_Base = [['Old Man House Exit (Bottom)', 'Old Man House Exit (Top)']]

Cave_Exits_Base = [['Elder House Exit (East)', 'Elder House Exit (West)'],
                   ['Two Brothers House Exit (East)', 'Two Brothers House Exit (West)'],
                   ['Death Mountain Return Cave Exit (West)', 'Death Mountain Return Cave Exit (East)'],
                   ['Fairy Ascension Cave Exit (Bottom)', 'Fairy Ascension Cave Exit (Top)'],
                   ['Bumper Cave Exit (Top)', 'Bumper Cave Exit (Bottom)'],
                   ['Hookshot Cave Exit (South)', 'Hookshot Cave Exit (North)']]

Cave_Exits_Base += [('Superbunny Cave Exit (Bottom)', 'Superbunny Cave Exit (Top)'),
                    ('Spiral Cave Exit (Top)', 'Spiral Cave Exit')]

Cave_Three_Exits_Base = [
    ('Spectacle Rock Cave Exit (Peak)', 'Spectacle Rock Cave Exit (Top)', 'Spectacle Rock Cave Exit'),
    ('Paradox Cave Exit (Top)', 'Paradox Cave Exit (Middle)', 'Paradox Cave Exit (Bottom)')
]

LW_Entrances = ['Elder House (East)',
                'Elder House (West)',
                'Two Brothers House (East)',
                'Two Brothers House (West)',
                'Old Man Cave (West)',
                'Old Man House (Bottom)',
                'Death Mountain Return Cave (West)',
                'Paradox Cave (Bottom)',
                'Paradox Cave (Middle)',
                'Paradox Cave (Top)',
                'Fairy Ascension Cave (Bottom)',
                'Fairy Ascension Cave (Top)',
                'Spiral Cave',
                'Spiral Cave (Bottom)']

DW_Entrances = ['Bumper Cave (Bottom)',
                'Superbunny Cave (Top)',
                'Superbunny Cave (Bottom)',
                'Hookshot Cave']

Bomb_Shop_Multi_Cave_Doors = ['Hyrule Castle Entrance (South)',
                              'Misery Mire',
                              'Thieves Town',
                              'Bumper Cave (Bottom)',
                              'Swamp Palace',
                              'Hyrule Castle Secret Entrance Stairs',
                              'Skull Woods First Section Door',
                              'Skull Woods Second Section Door (East)',
                              'Skull Woods Second Section Door (West)',
                              'Skull Woods Final Section',
                              'Ice Palace',
                              'Turtle Rock',
                              'Dark Death Mountain Ledge (West)',
                              'Dark Death Mountain Ledge (East)',
                              'Superbunny Cave (Top)',
                              'Superbunny Cave (Bottom)',
                              'Hookshot Cave',
                              'Ganons Tower',
                              'Desert Palace Entrance (South)',
                              'Tower of Hera',
                              'Two Brothers House (West)',
                              'Old Man Cave (East)',
                              'Old Man House (Bottom)',
                              'Old Man House (Top)',
                              'Death Mountain Return Cave (East)',
                              'Death Mountain Return Cave (West)',
                              'Spectacle Rock Cave Peak',
                              'Spectacle Rock Cave',
                              'Spectacle Rock Cave (Bottom)',
                              'Paradox Cave (Bottom)',
                              'Paradox Cave (Middle)',
                              'Paradox Cave (Top)',
                              'Fairy Ascension Cave (Bottom)',
                              'Fairy Ascension Cave (Top)',
                              'Spiral Cave',
                              'Spiral Cave (Bottom)',
                              'Palace of Darkness',
                              'Hyrule Castle Entrance (West)',
                              'Hyrule Castle Entrance (East)',
                              'Agahnims Tower',
                              'Desert Palace Entrance (West)',
                              'Desert Palace Entrance (North)'
                              # all entrances below this line would be possible for blacksmith_hut
                              # if it were not for dwarf checking multi-entrance caves
                              ]

Blacksmith_Multi_Cave_Doors = ['Eastern Palace',
                               'Elder House (East)',
                               'Elder House (West)',
                               'Two Brothers House (East)',
                               'Old Man Cave (West)',
                               'Sanctuary',
                               'Lumberjack Tree Cave',
                               'Lost Woods Hideout Stump',
                               'North Fairy Cave',
                               'Bat Cave Cave',
                               'Kakariko Well Cave']

LW_Single_Cave_Doors = ['Blinds Hideout',
                        'Lake Hylia Fairy',
                        'Light Hype Fairy',
                        'Desert Fairy',
                        'Chicken House',
                        'Aginahs Cave',
                        'Sahasrahlas Hut',
                        'Cave Shop (Lake Hylia)',
                        'Blacksmiths Hut',
                        'Sick Kids House',
                        'Lost Woods Gamble',
                        'Fortune Teller (Light)',
                        'Snitch Lady (East)',
                        'Snitch Lady (West)',
                        'Bush Covered House',
                        'Tavern (Front)',
                        'Light World Bomb Hut',
                        'Kakariko Shop',
                        'Mini Moldorm Cave',
                        'Long Fairy Cave',
                        'Good Bee Cave',
                        '20 Rupee Cave',
                        '50 Rupee Cave',
                        'Ice Rod Cave',
                        'Library',
                        'Potion Shop',
                        'Dam',
                        'Lumberjack House',
                        'Lake Hylia Fortune Teller',
                        'Kakariko Gamble Game',
                        'Waterfall of Wishing',
                        'Capacity Upgrade',
                        'Bonk Rock Cave',
                        'Graveyard Cave',
                        'Checkerboard Cave',
                        'Cave 45',
                        'Kings Grave',
                        'Bonk Fairy (Light)',
                        'Hookshot Fairy',
                        'Mimic Cave']

DW_Single_Cave_Doors = ['Bonk Fairy (Dark)',
                        'Dark Sanctuary Hint',
                        'Dark Lake Hylia Fairy',
                        'C-Shaped House',
                        'Big Bomb Shop',
                        'Dark Death Mountain Fairy',
                        'Dark Lake Hylia Shop',
                        'Dark World Shop',
                        'Red Shield Shop',
                        'Mire Shed',
                        'East Dark World Hint',
                        'Dark Desert Hint',
                        'Spike Cave',
                        'Palace of Darkness Hint',
                        'Dark Lake Hylia Ledge Spike Cave',
                        'Cave Shop (Dark Death Mountain)',
                        'Dark World Potion Shop',
                        'Pyramid Fairy',
                        'Archery Game',
                        'Dark World Lumberjack Shop',
                        'Hype Cave',
                        'Brewery',
                        'Dark Lake Hylia Ledge Hint',
                        'Chest Game',
                        'Dark Desert Fairy',
                        'Dark Lake Hylia Ledge Fairy',
                        'Fortune Teller (Dark)',
                        'Dark World Hammer Peg Cave']

Blacksmith_Single_Cave_Doors = ['Blinds Hideout',
                                'Lake Hylia Fairy',
                                'Light Hype Fairy',
                                'Desert Fairy',
                                'Chicken House',
                                'Aginahs Cave',
                                'Sahasrahlas Hut',
                                'Cave Shop (Lake Hylia)',
                                'Blacksmiths Hut',
                                'Sick Kids House',
                                'Lost Woods Gamble',
                                'Fortune Teller (Light)',
                                'Snitch Lady (East)',
                                'Snitch Lady (West)',
                                'Bush Covered House',
                                'Tavern (Front)',
                                'Light World Bomb Hut',
                                'Kakariko Shop',
                                'Mini Moldorm Cave',
                                'Long Fairy Cave',
                                'Good Bee Cave',
                                '20 Rupee Cave',
                                '50 Rupee Cave',
                                'Ice Rod Cave',
                                'Library',
                                'Potion Shop',
                                'Dam',
                                'Lumberjack House',
                                'Lake Hylia Fortune Teller',
                                'Kakariko Gamble Game']

Bomb_Shop_Single_Cave_Doors = ['Waterfall of Wishing',
                               'Capacity Upgrade',
                               'Bonk Rock Cave',
                               'Graveyard Cave',
                               'Checkerboard Cave',
                               'Cave 45',
                               'Kings Grave',
                               'Bonk Fairy (Light)',
                               'Hookshot Fairy',
                               'East Dark World Hint',
                               'Palace of Darkness Hint',
                               'Dark Lake Hylia Fairy',
                               'Dark Lake Hylia Ledge Fairy',
                               'Dark Lake Hylia Ledge Spike Cave',
                               'Dark Lake Hylia Ledge Hint',
                               'Hype Cave',
                               'Bonk Fairy (Dark)',
                               'Brewery',
                               'C-Shaped House',
                               'Chest Game',
                               'Dark World Hammer Peg Cave',
                               'Red Shield Shop',
                               'Dark Sanctuary Hint',
                               'Fortune Teller (Dark)',
                               'Dark World Shop',
                               'Dark World Lumberjack Shop',
                               'Dark World Potion Shop',
                               'Archery Game',
                               'Mire Shed',
                               'Dark Desert Hint',
                               'Dark Desert Fairy',
                               'Spike Cave',
                               'Cave Shop (Dark Death Mountain)',
                               'Dark Death Mountain Fairy',
                               'Mimic Cave',
                               'Big Bomb Shop',
                               'Dark Lake Hylia Shop']

Single_Cave_Doors = ['Pyramid Fairy']

Single_Cave_Targets = ['Blinds Hideout',
                       'Bonk Fairy (Light)',
                       'Lake Hylia Healer Fairy',
                       'Swamp Healer Fairy',
                       'Desert Healer Fairy',
                       'Kings Grave',
                       'Chicken House',
                       'Aginahs Cave',
                       'Sahasrahlas Hut',
                       'Cave Shop (Lake Hylia)',
                       'Sick Kids House',
                       'Lost Woods Gamble',
                       'Fortune Teller (Light)',
                       'Snitch Lady (East)',
                       'Snitch Lady (West)',
                       'Bush Covered House',
                       'Tavern (Front)',
                       'Light World Bomb Hut',
                       'Kakariko Shop',
                       'Cave 45',
                       'Graveyard Cave',
                       'Checkerboard Cave',
                       'Mini Moldorm Cave',
                       'Long Fairy Cave',
                       'Good Bee Cave',
                       '20 Rupee Cave',
                       '50 Rupee Cave',
                       'Ice Rod Cave',
                       'Bonk Rock Cave',
                       'Library',
                       'Potion Shop',
                       'Hookshot Fairy',
                       'Waterfall of Wishing',
                       'Capacity Upgrade',
                       'Pyramid Fairy',
                       'East Dark World Hint',
                       'Palace of Darkness Hint',
                       'Dark Lake Hylia Healer Fairy',
                       'Dark Lake Hylia Ledge Healer Fairy',
                       'Dark Lake Hylia Ledge Spike Cave',
                       'Dark Lake Hylia Ledge Hint',
                       'Hype Cave',
                       'Bonk Fairy (Dark)',
                       'Brewery',
                       'C-Shaped House',
                       'Chest Game',
                       'Dark World Hammer Peg Cave',
                       'Red Shield Shop',
                       'Dark Sanctuary Hint',
                       'Fortune Teller (Dark)',
                       'Village of Outcasts Shop',
                       'Dark Lake Hylia Shop',
                       'Dark World Lumberjack Shop',
                       'Archery Game',
                       'Mire Shed',
                       'Dark Desert Hint',
                       'Dark Desert Healer Fairy',
                       'Spike Cave',
                       'Cave Shop (Dark Death Mountain)',
                       'Dark Death Mountain Healer Fairy',
                       'Mimic Cave',
                       'Dark World Potion Shop',
                       'Lumberjack House',
                       'Lake Hylia Fortune Teller',
                       'Kakariko Gamble Game',
                       'Dam']

Inverted_LW_Dungeon_Entrances = ['Desert Palace Entrance (South)',
                                 'Eastern Palace',
                                 'Tower of Hera',
                                 'Hyrule Castle Entrance (West)',
                                 'Hyrule Castle Entrance (East)']

Inverted_DW_Dungeon_Entrances = ['Thieves Town',
                                 'Skull Woods Final Section',
                                 'Ice Palace',
                                 'Misery Mire',
                                 'Palace of Darkness',
                                 'Swamp Palace',
                                 'Turtle Rock',
                                 'Dark Death Mountain Ledge (West)',
                                 'Dark Death Mountain Ledge (East)',
                                 'Turtle Rock Isolated Ledge Entrance',
                                 'Inverted Agahnims Tower']

Inverted_LW_Dungeon_Entrances_Must_Exit = ['Desert Palace Entrance (East)']

Inverted_Dungeon_Exits_Base = [['Desert Palace Exit (South)', 'Desert Palace Exit (West)', 'Desert Palace Exit (East)'],
                               'Desert Palace Exit (North)',
                               'Eastern Palace Exit',
                               'Tower of Hera Exit',
                               'Thieves Town Exit',
                               'Skull Woods Final Section Exit',
                               'Ice Palace Exit',
                               'Misery Mire Exit',
                               'Palace of Darkness Exit',
                               'Swamp Palace Exit',
                               'Inverted Agahnims Tower Exit',
                               ['Turtle Rock Ledge Exit (East)',
                                'Turtle Rock Exit (Front)', 'Turtle Rock Ledge Exit (West)',
                                'Turtle Rock Isolated Ledge Exit']]

Inverted_LW_Entrances_Must_Exit = ['Death Mountain Return Cave (West)',
                                   'Two Brothers House (West)']

Inverted_Two_Door_Caves_Directional = [('Old Man Cave (West)', 'Death Mountain Return Cave (West)'),
                                       ('Two Brothers House (East)', 'Two Brothers House (West)')]

Inverted_Two_Door_Caves = [('Elder House (East)', 'Elder House (West)'),
                           ('Superbunny Cave (Bottom)', 'Superbunny Cave (Top)'),
                           ('Hookshot Cave', 'Hookshot Cave Back Entrance')]

Inverted_Old_Man_Entrances = ['Dark Death Mountain Fairy',
                              'Spike Cave']

Inverted_LW_Entrances = ['Elder House (East)',
                         'Elder House (West)',
                         'Two Brothers House (East)',
                         'Old Man Cave (East)',
                         'Old Man Cave (West)',
                         'Old Man House (Bottom)',
                         'Old Man House (Top)',
                         'Death Mountain Return Cave (East)',
                         'Paradox Cave (Bottom)',
                         'Paradox Cave (Middle)',
                         'Paradox Cave (Top)',
                         'Spectacle Rock Cave',
                         'Spectacle Rock Cave Peak',
                         'Spectacle Rock Cave (Bottom)',
                         'Fairy Ascension Cave (Bottom)',
                         'Fairy Ascension Cave (Top)',
                         'Spiral Cave',
                         'Spiral Cave (Bottom)']

Inverted_DW_Entrances = ['Bumper Cave (Bottom)',
                         'Superbunny Cave (Top)',
                         'Superbunny Cave (Bottom)',
                         'Hookshot Cave',
                         'Hookshot Cave Back Entrance']

Inverted_Bomb_Shop_Multi_Cave_Doors = ['Hyrule Castle Entrance (South)',
                                       'Misery Mire',
                                       'Thieves Town',
                                       'Bumper Cave (Bottom)',
                                       'Swamp Palace',
                                       'Hyrule Castle Secret Entrance Stairs',
                                       'Skull Woods First Section Door',
                                       'Skull Woods Second Section Door (East)',
                                       'Skull Woods Second Section Door (West)',
                                       'Skull Woods Final Section',
                                       'Ice Palace',
                                       'Turtle Rock',
                                       'Dark Death Mountain Ledge (West)',
                                       'Dark Death Mountain Ledge (East)',
                                       'Superbunny Cave (Top)',
                                       'Superbunny Cave (Bottom)',
                                       'Hookshot Cave',
                                       'Inverted Agahnims Tower',
                                       'Desert Palace Entrance (South)',
                                       'Tower of Hera',
                                       'Two Brothers House (West)',
                                       'Old Man Cave (East)',
                                       'Old Man House (Bottom)',
                                       'Old Man House (Top)',
                                       'Death Mountain Return Cave (East)',
                                       'Death Mountain Return Cave (West)',
                                       'Spectacle Rock Cave Peak',
                                       'Paradox Cave (Bottom)',
                                       'Paradox Cave (Middle)',
                                       'Paradox Cave (Top)',
                                       'Fairy Ascension Cave (Bottom)',
                                       'Fairy Ascension Cave (Top)',
                                       'Spiral Cave',
                                       'Spiral Cave (Bottom)',
                                       'Palace of Darkness',
                                       'Hyrule Castle Entrance (West)',
                                       'Hyrule Castle Entrance (East)',
                                       'Inverted Ganons Tower',
                                       'Desert Palace Entrance (West)',
                                       'Desert Palace Entrance (North)']

Inverted_Blacksmith_Multi_Cave_Doors = Blacksmith_Multi_Cave_Doors  # same as non-inverted

Inverted_LW_Single_Cave_Doors = LW_Single_Cave_Doors + ['Inverted Big Bomb Shop']

Inverted_DW_Single_Cave_Doors = ['Bonk Fairy (Dark)',
                                 'Inverted Dark Sanctuary',
                                 'Inverted Links House',
                                 'Dark Lake Hylia Fairy',
                                 'C-Shaped House',
                                 'Bumper Cave (Top)',
                                 'Dark Lake Hylia Shop',
                                 'Dark World Shop',
                                 'Red Shield Shop',
                                 'Mire Shed',
                                 'East Dark World Hint',
                                 'Dark Desert Hint',
                                 'Palace of Darkness Hint',
                                 'Dark Lake Hylia Ledge Spike Cave',
                                 'Cave Shop (Dark Death Mountain)',
                                 'Dark World Potion Shop',
                                 'Pyramid Fairy',
                                 'Archery Game',
                                 'Dark World Lumberjack Shop',
                                 'Hype Cave',
                                 'Brewery',
                                 'Dark Lake Hylia Ledge Hint',
                                 'Chest Game',
                                 'Dark Desert Fairy',
                                 'Dark Lake Hylia Ledge Fairy',
                                 'Fortune Teller (Dark)',
                                 'Dark World Hammer Peg Cave']

Inverted_Bomb_Shop_Single_Cave_Doors = ['Waterfall of Wishing',
                                        'Capacity Upgrade',
                                        'Bonk Rock Cave',
                                        'Graveyard Cave',
                                        'Checkerboard Cave',
                                        'Cave 45',
                                        'Kings Grave',
                                        'Bonk Fairy (Light)',
                                        'Hookshot Fairy',
                                        'East Dark World Hint',
                                        'Palace of Darkness Hint',
                                        'Dark Lake Hylia Fairy',
                                        'Dark Lake Hylia Ledge Fairy',
                                        'Dark Lake Hylia Ledge Spike Cave',
                                        'Dark Lake Hylia Ledge Hint',
                                        'Hype Cave',
                                        'Bonk Fairy (Dark)',
                                        'Brewery',
                                        'C-Shaped House',
                                        'Chest Game',
                                        'Dark World Hammer Peg Cave',
                                        'Red Shield Shop',
                                        'Inverted Dark Sanctuary',
                                        'Fortune Teller (Dark)',
                                        'Dark World Shop',
                                        'Dark World Lumberjack Shop',
                                        'Dark World Potion Shop',
                                        'Archery Game',
                                        'Mire Shed',
                                        'Dark Desert Hint',
                                        'Dark Desert Fairy',
                                        'Spike Cave',
                                        'Cave Shop (Dark Death Mountain)',
                                        'Bumper Cave (Top)',
                                        'Mimic Cave',
                                        'Dark Lake Hylia Shop',
                                        'Inverted Links House',
                                        'Inverted Big Bomb Shop']

Inverted_Single_Cave_Targets = ['Blinds Hideout',
                                'Bonk Fairy (Light)',
                                'Lake Hylia Healer Fairy',
                                'Swamp Healer Fairy',
                                'Desert Healer Fairy',
                                'Kings Grave',
                                'Chicken House',
                                'Aginahs Cave',
                                'Sahasrahlas Hut',
                                'Cave Shop (Lake Hylia)',
                                'Sick Kids House',
                                'Lost Woods Gamble',
                                'Fortune Teller (Light)',
                                'Snitch Lady (East)',
                                'Snitch Lady (West)',
                                'Bush Covered House',
                                'Tavern (Front)',
                                'Light World Bomb Hut',
                                'Kakariko Shop',
                                'Cave 45',
                                'Graveyard Cave',
                                'Checkerboard Cave',
                                'Mini Moldorm Cave',
                                'Long Fairy Cave',
                                'Good Bee Cave',
                                '20 Rupee Cave',
                                '50 Rupee Cave',
                                'Ice Rod Cave',
                                'Bonk Rock Cave',
                                'Library',
                                'Potion Shop',
                                'Hookshot Fairy',
                                'Waterfall of Wishing',
                                'Capacity Upgrade',
                                'Pyramid Fairy',
                                'East Dark World Hint',
                                'Palace of Darkness Hint',
                                'Dark Lake Hylia Healer Fairy',
                                'Dark Lake Hylia Ledge Healer Fairy',
                                'Dark Lake Hylia Ledge Spike Cave',
                                'Dark Lake Hylia Ledge Hint',
                                'Hype Cave',
                                'Bonk Fairy (Dark)',
                                'Brewery',
                                'C-Shaped House',
                                'Chest Game',
                                'Dark World Hammer Peg Cave',
                                'Red Shield Shop',
                                'Fortune Teller (Dark)',
                                'Village of Outcasts Shop',
                                'Dark Lake Hylia Shop',
                                'Dark World Lumberjack Shop',
                                'Archery Game',
                                'Mire Shed',
                                'Dark Desert Hint',
                                'Dark Desert Healer Fairy',
                                'Spike Cave',
                                'Cave Shop (Dark Death Mountain)',
                                'Dark Death Mountain Healer Fairy',
                                'Mimic Cave',
                                'Dark World Potion Shop',
                                'Lumberjack House',
                                'Lake Hylia Fortune Teller',
                                'Kakariko Gamble Game',
                                'Dam']

# in inverted we put dark sanctuary in west dark world for now
Inverted_Dark_Sanctuary_Doors = ['Inverted Dark Sanctuary',
                                 'Fortune Teller (Dark)',
                                 'Brewery',
                                 'C-Shaped House',
                                 'Chest Game',
                                 'Dark World Lumberjack Shop',
                                 'Red Shield Shop',
                                 'Bumper Cave (Bottom)',
                                 'Bumper Cave (Top)',
                                 'Thieves Town']

Isolated_LH_Doors = ['Kings Grave',
                     'Waterfall of Wishing',
                     'Desert Palace Entrance (South)',
                     'Desert Palace Entrance (North)',
                     'Capacity Upgrade',
                     'Ice Palace',
                     'Skull Woods Final Section',
                     'Dark World Hammer Peg Cave',
                     'Turtle Rock Isolated Ledge Entrance']

