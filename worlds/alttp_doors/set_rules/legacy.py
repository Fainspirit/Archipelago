from worlds.alttp.UnderworldGlitchRules import underworld_glitches_rules
from worlds.alttp_doors.legacy.rules.overworld_glitch_rules import no_logic_rules, overworld_glitches_rules
from worlds.alttp_doors.legacy.rules.rules import global_rules, dungeon_boss_rules, default_rules, open_rules, \
    standard_rules, inverted_rules, no_glitches_rules, fake_flipper_rules, set_big_bomb_rules, \
    mirrorless_path_to_castle_courtyard, set_inverted_big_bomb_rules, set_trock_key_rules, set_bunny_rules
from worlds.generic.Rules import add_rule, set_rule


def set_rules(world):
    player = world.player
    world = world.world
    # TODO fix this
    if False and world.logic[player] == 'nologic':
        # if player == next(player_id for player_id in world.get_game_players("A Link to the Past")
        #                   if world.logic[player_id] == 'nologic'):  # only warn one time
        #     logging.info(
        #         'WARNING! Seeds generated under this logic often require major glitches and may be impossible!')

        if world.players == 1:
            world.get_region('Menu', player).can_reach_private = lambda state: True
            no_logic_rules(world, player)
            for exit in world.get_region('Menu', player).exits:
                exit.hide_path = True
            return
        else:
            # Set access rules according to max glitches for multiworld progression.
            # Set accessibility to none, and shuffle assuming the no logic players can always win
            world.accessibility[player] = world.accessibility[player].from_text("minimal")
            world.progression_balancing[player].value = False

    else:
        world.completion_condition[player] = lambda state: state.has('Triforce', player)

    global_rules(world, player)
    dungeon_boss_rules(world, player)

    if world.mode[player] != 'inverted':
        default_rules(world, player)

    if world.mode[player] == 'open':
        open_rules(world, player)
    elif world.mode[player] == 'standard':
        standard_rules(world, player)
    elif world.mode[player] == 'inverted':
        open_rules(world, player)
        inverted_rules(world, player)
    else:
        raise NotImplementedError(f'World state {world.mode[player]} is not implemented yet')
    # TODO fix this
    if True or world.logic[player] == 'noglitches':
        no_glitches_rules(world, player)
    elif world.logic[player] == 'owglitches':
        # Initially setting no_glitches_rules to set the baseline rules for some
        # entrances. The overworld_glitches_rules set is primarily additive.
        no_glitches_rules(world, player)
        fake_flipper_rules(world, player)
        overworld_glitches_rules(world, player)
    elif world.logic[player] in ['hybridglitches', 'nologic']:
        no_glitches_rules(world, player)
        fake_flipper_rules(world, player)
        overworld_glitches_rules(world, player)
        underworld_glitches_rules(world, player)
    elif world.logic[player] == 'minorglitches':
        no_glitches_rules(world, player)
        fake_flipper_rules(world, player)
    else:
        raise NotImplementedError(f'Not implemented yet: Logic - {world.logic[player]}')
    # Todo fix
    if False and world.goal[player] == 'bosses':
        # require all bosses to beat ganon
        add_rule(world.get_location('Ganon', player), lambda state: state.can_reach('Master Sword Pedestal', 'Location', player) and state.has('Beat Agahnim 1', player) and state.has('Beat Agahnim 2', player) and state.has_crystals(7, player))
    elif True or world.goal[player] == 'ganon':
        # require aga2 to beat ganon
        add_rule(world.get_location('Ganon', player), lambda state: state.has('Beat Agahnim 2', player))

    if world.mode[player] != 'inverted':
        set_big_bomb_rules(world, player)
        if world.logic[player] in {'owglitches', 'hybridglitches', 'nologic'} and world.shuffle[player] not in {'insanity', 'insanity_legacy', 'madness'}:
            path_to_courtyard = mirrorless_path_to_castle_courtyard(world, player)
            add_rule(world.get_entrance('Pyramid Fairy', player), lambda state: state.world.get_entrance('Dark Death Mountain Offset Mirror', player).can_reach(state) and all(rule(state) for rule in path_to_courtyard), 'or')
    else:
        set_inverted_big_bomb_rules(world, player)

    # if swamp and dam have not been moved we require mirror for swamp palace
    # however there is mirrorless swamp in hybrid MG, so we don't necessarily want this. HMG handles this requirement itself.
    if not world.swamp_patch_required[player] and world.logic[player] not in ['hybridglitches', 'nologic']:
        add_rule(world.get_entrance('Swamp Palace Moat', player), lambda state: state.has('Magic Mirror', player))

    # GT Entrance may be required for Turtle Rock for OWG and < 7 required
    ganons_tower = world.get_entrance('Inverted Ganons Tower' if world.mode[player] == 'inverted' else 'Ganons Tower', player)
    if world.crystals_needed_for_gt[player] == 7 and not (world.logic[player] in ['owglitches', 'hybridglitches', 'nologic'] and world.mode[player] != 'inverted'):
        set_rule(ganons_tower, lambda state: False)

    set_trock_key_rules(world, player)

    set_rule(ganons_tower, lambda state: state.has_crystals(state.world.crystals_needed_for_gt[player], player))
    if world.mode[player] != 'inverted' and world.logic[player] in ['owglitches', 'hybridglitches', 'nologic']:
        add_rule(world.get_entrance('Ganons Tower', player), lambda state: state.world.get_entrance('Ganons Tower Ascent', player).can_reach(state), 'or')

    set_bunny_rules(world, player, world.mode[player] == 'inverted')