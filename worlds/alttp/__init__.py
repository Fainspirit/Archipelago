import random
import logging
import threading
import typing
from argparse import Namespace

import Options
from BaseClasses import Item, CollectionState
from .mode_handler import ModeHandler

from ..AutoWorld import World, LogicMixin

from . import write_rom

# Methods from before the refactor
from .standard.options import options, smallkey_shuffle
from .legacy.Items import as_dict_item_table, item_name_groups, item_table
from worlds.alttp.generic.regions import lookup_name_to_id, create_regions, mark_light_world_regions
from .legacy.Rules import set_rules
from .legacy.ItemPool import generate_itempool, difficulties
from .legacy.Dungeons import create_dungeons
from .legacy.InvertedRegions import create_inverted_regions, mark_dark_world_regions

from .generic.shop_fill import create_shops, ShopSlotFill
from .generic.SubClasses import ALttPItem

from .entrance_randomizer.EntranceShuffle import link_entrances, link_inverted_entrances, plando_connect

lttp_logger = logging.getLogger("A Link to the Past")


class ALTTPWorld(World):
    """
    The Legend of Zelda: A Link to the Past is an action/adventure game. Take on the role of
    Link, a boy who is destined to save the land of Hyrule. Delve through three palaces and nine
    dungeons on your quest to rescue the descendents of the seven wise men and defeat the evil
    Ganon!
    """
    game: str = "A Link to the Past"
    can_self_init = True

    # Based on settings, built options list
    # This gets built for the class on autoworld init, so there may be no need to
    options = ModeHandler.build_options(True, True, False)

    topology_present = True
    item_name_groups = item_name_groups
    hint_blacklist = {"Triforce"}

    item_name_to_id = {name: data.item_code for name, data in item_table.items() if type(data.item_code) == int}
    location_name_to_id = lookup_name_to_id

    data_version = 8
    remote_items: bool = False
    remote_start_inventory: bool = False

    set_rules = set_rules

    create_items = generate_itempool

    def __init__(self, *args, **kwargs):
        self.dungeon_local_item_names = set()
        self.dungeon_specific_item_names = set()
        self.rom_name_available_event = threading.Event()
        self.has_progressive_bows = False
        super(ALTTPWorld, self).__init__(*args, **kwargs)


    # Selected options contain both global scope and per player
    def handle_option_values(self, args_from_world: typing.Dict[str, object]):
        """Build the world's store of the options that were rolled for it."""

        # For each option that this game cares about
        for opt_name, opt_obj in self.options.items():

            if opt_name in args_from_world:
                val = args_from_world[opt_name][self.player]
                opt_obj.value = val

                # TODO: Remove Option.keep_value (if there is truly no use for it)
                #if opt_obj.keep_value:
                # Save the value to this autoworld
                self.saved_options[opt_name] = val
            else:
                raise Exception(f"Tried to handle {opt_name}, which isn't defined for A Link to the Past!")

    def generate_early(self):
        player = self.player
        world = self.world

        # system for sharing ER layouts
        self.er_seed = str(world.random.randint(0, 2 ** 64))

        # TODO: Verify shuffle options + add entrance_shuffle option
        # If shuffle options have dash
        if False and "-" in world.autoworlds[player].saved_options["shuffle"]:
            shuffle, seed = world.shuffle[player].split("-", 1)
            world.shuffle[player] = shuffle

            # Determine what seed to use for ER
            if shuffle == "vanilla":
                self.er_seed = "vanilla"

            # If the entrance randomizer should be seeded identically (for a race)
            elif self.seed.startswith("group-") or world.is_race:
                self.er_seed = get_same_seed(world, (
                    shuffle, seed, world.retro[player], world.mode[player], world.logic[player]))
            else:  # not a race or group seed, use set seed as is.
                self.er_seed = seed

        # TODO this
        #elif world.shuffle[player] == "vanilla":
        elif False and self.saved_options["entrance_shuffle"] == "vanilla":
            self.er_seed = "vanilla"

        # Create custom groups for where items can be placed
        self.local_items = {}
        self.non_local_items = {}

        # Parse options to figure out which dungeon items will be where
        self.assign_dungeon_item_groups()

    # Group where the dungeon items will go
    # Local, non-local
    def assign_dungeon_item_groups(self):
        player = self.player
        world = self.world

        # For each type of dungeon item
        for dungeon_item in ["smallkey_shuffle", "bigkey_shuffle", "compass_shuffle", "map_shuffle"]:
            #option = getattr(world, dungeon_item)[player]
            option = self.saved_options[dungeon_item]

            # Declare placing group locally
            if option == "own_world":
                # TODO: make sure world has local items for compat (?), use local here
                #world.local_items[player].value |= self.item_name_groups[option.item_name_group]
                self.local_items.value |= self.item_name_groups[option.item_name_group]
            # Declare placing group not locally
            elif option == "different_world":
                world.non_local_items[player].value |= self.item_name_groups[option.item_name_group]
            # Declare placing item in a dungeon
            elif option.in_dungeon:
                self.dungeon_local_item_names |= self.item_name_groups[option.item_name_group]
                # Declare placing item in a specific dungeon
                if option == "original_dungeon":
                    self.dungeon_specific_item_names |= self.item_name_groups[option.item_name_group]


    def create_regions(self):
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
            mark_light_world_regions(world, player)
        else:
            link_inverted_entrances(world, player)
            mark_dark_world_regions(world, player)

        world.random = old_random
        plando_connect(world, player)

    def collect_item(self, state: CollectionState, item: Item, remove=False):
        item_name = item.name
        if item_name.startswith('Progressive '):
            if remove:
                if 'Sword' in item_name:
                    if state.has('Golden Sword', item.player):
                        return 'Golden Sword'
                    elif state.has('Tempered Sword', item.player):
                        return 'Tempered Sword'
                    elif state.has('Master Sword', item.player):
                        return 'Master Sword'
                    elif state.has('Fighter Sword', item.player):
                        return 'Fighter Sword'
                    else:
                        return None
                elif 'Glove' in item.name:
                    if state.has('Titans Mitts', item.player):
                        return 'Titans Mitts'
                    elif state.has('Power Glove', item.player):
                        return 'Power Glove'
                    else:
                        return None
                elif 'Shield' in item_name:
                    if state.has('Mirror Shield', item.player):
                        return 'Mirror Shield'
                    elif state.has('Red Shield', item.player):
                        return 'Red Shield'
                    elif state.has('Blue Shield', item.player):
                        return 'Blue Shield'
                    else:
                        return None
                elif 'Bow' in item_name:
                    if state.has('Silver Bow', item.player):
                        return 'Silver Bow'
                    elif state.has('Bow', item.player):
                        return 'Bow'
                    else:
                        return None
            else:
                if 'Sword' in item_name:
                    if state.has('Golden Sword', item.player):
                        pass
                    elif state.has('Tempered Sword', item.player) and self.world.difficulty_requirements[
                        item.player].progressive_sword_limit >= 4:
                        return 'Golden Sword'
                    elif state.has('Master Sword', item.player) and self.world.difficulty_requirements[
                        item.player].progressive_sword_limit >= 3:
                        return 'Tempered Sword'
                    elif state.has('Fighter Sword', item.player) and self.world.difficulty_requirements[item.player].progressive_sword_limit >= 2:
                        return 'Master Sword'
                    elif self.world.difficulty_requirements[item.player].progressive_sword_limit >= 1:
                        return 'Fighter Sword'
                elif 'Glove' in item_name:
                    if state.has('Titans Mitts', item.player):
                        return
                    elif state.has('Power Glove', item.player):
                        return 'Titans Mitts'
                    else:
                        return 'Power Glove'
                elif 'Shield' in item_name:
                    if state.has('Mirror Shield', item.player):
                        return
                    elif state.has('Red Shield', item.player) and self.world.difficulty_requirements[item.player].progressive_shield_limit >= 3:
                        return 'Mirror Shield'
                    elif state.has('Blue Shield', item.player)  and self.world.difficulty_requirements[item.player].progressive_shield_limit >= 2:
                        return 'Red Shield'
                    elif self.world.difficulty_requirements[item.player].progressive_shield_limit >= 1:
                        return 'Blue Shield'
                elif 'Bow' in item_name:
                    if state.has('Silver Bow', item.player):
                        return
                    elif state.has('Bow', item.player) and (self.world.difficulty_requirements[item.player].progressive_bow_limit >= 2
                        or self.world.logic[item.player] == 'noglitches'
                        or self.world.swordless[item.player]): # modes where silver bow is always required for ganon
                        return 'Silver Bow'
                    elif self.world.difficulty_requirements[item.player].progressive_bow_limit >= 1:
                        return 'Bow'
        elif item.advancement:
            return item_name

    def pre_fill(self):
        from Fill import fill_restrictive, FillError
        attempts = 5
        world = self.world
        player = self.player
        all_state = world.get_all_state(use_cache=True)
        crystals = [self.create_item(name) for name in ['Red Pendant', 'Blue Pendant', 'Green Pendant', 'Crystal 1', 'Crystal 2', 'Crystal 3', 'Crystal 4', 'Crystal 7', 'Crystal 5', 'Crystal 6']]
        crystal_locations = [world.get_location('Turtle Rock - Prize', player),
                             world.get_location('Eastern Palace - Prize', player),
                             world.get_location('Desert Palace - Prize', player),
                             world.get_location('Tower of Hera - Prize', player),
                             world.get_location('Palace of Darkness - Prize', player),
                             world.get_location('Thieves\' Town - Prize', player),
                             world.get_location('Skull Woods - Prize', player),
                             world.get_location('Swamp Palace - Prize', player),
                             world.get_location('Ice Palace - Prize', player),
                             world.get_location('Misery Mire - Prize', player)]
        placed_prizes = {loc.item.name for loc in crystal_locations if loc.item}
        unplaced_prizes = [crystal for crystal in crystals if crystal.name not in placed_prizes]
        empty_crystal_locations = [loc for loc in crystal_locations if not loc.item]
        for attempt in range(attempts):
            try:
                prizepool = unplaced_prizes.copy()
                prize_locs = empty_crystal_locations.copy()
                world.random.shuffle(prize_locs)
                fill_restrictive(world, all_state, prize_locs, prizepool, True, lock=True)
            except FillError as e:
                lttp_logger.exception("Failed to place dungeon prizes (%s). Will retry %s more times", e,
                                                attempts - attempt)
                for location in empty_crystal_locations:
                    location.item = None
                continue
            break
        else:
            raise FillError('Unable to place dungeon prizes')

    @classmethod
    def stage_pre_fill(cls, world):
        from .legacy.Dungeons import fill_dungeons_restrictive
        fill_dungeons_restrictive(cls, world)

    @classmethod
    def stage_post_fill(cls, world):
        ShopSlotFill(world)

    def generate_output(self, output_directory: str):
        return write_rom.write_rom(self, output_directory)

    def modify_multidata(self, multidata: dict):
        import base64
        # wait for self.rom_name to be available.
        self.rom_name_available_event.wait()
        rom_name = getattr(self, "rom_name", None)
        # we skip in case of error, so that the original error in the output thread is the one that gets raised
        if rom_name:
            new_name = base64.b64encode(bytes(self.rom_name)).decode()
            payload = multidata["connect_names"][self.world.player_names[self.player]]
            multidata["connect_names"][new_name] = payload
            del (multidata["connect_names"][self.world.player_names[self.player]])

    def get_required_client_version(self) -> tuple:
        return max((0, 1, 4), super(ALTTPWorld, self).get_required_client_version())

    def create_item(self, name: str) -> Item:
        return ALttPItem(name, self.player, **as_dict_item_table[name])

    @classmethod
    def stage_fill_hook(cls, world, progitempool, nonexcludeditempool, localrestitempool, nonlocalrestitempool,
                        restitempool, fill_locations):
        trash_counts = {}
        standard_keyshuffle_players = set()
        for player in world.get_game_players("A Link to the Past"):
            if world.mode[player] == 'standard' and world.smallkey_shuffle[player] \
                    and world.smallkey_shuffle[player] != smallkey_shuffle.option_universal:
                standard_keyshuffle_players.add(player)
            if not world.ganonstower_vanilla[player] or \
                    world.logic[player] in {'owglitches', 'hybridglitches', "nologic"}:
                pass
            elif 'triforcehunt' in world.goal[player] and ('local' in world.goal[player] or world.players == 1):
                trash_counts[player] = world.random.randint(world.crystals_needed_for_gt[player] * 2,
                                                            world.crystals_needed_for_gt[player] * 4)
            else:
                trash_counts[player] = world.random.randint(0, world.crystals_needed_for_gt[player] * 2)

        # Make sure the escape small key is placed first in standard with key shuffle to prevent running out of spots
        # TODO: this might be worthwhile to introduce as generic option for various games and then optimize it
        if standard_keyshuffle_players:
            viable = []
            for location in world.get_locations():
                if location.player in standard_keyshuffle_players \
                        and location.item is None \
                        and location.can_reach(world.state):
                    viable.append(location)
            world.random.shuffle(viable)
            for player in standard_keyshuffle_players:
                key = world.create_item("Small Key (Hyrule Castle)", player)
                loc = viable.pop()
                loc.place_locked_item(key)
                fill_locations.remove(loc)
            world.random.shuffle(fill_locations)
            # TODO: investigate not creating the key in the first place
            progitempool[:] = [item for item in progitempool if
                               item.player not in standard_keyshuffle_players or
                               item.name != "Small Key (Hyrule Castle)"]

        if trash_counts:
            locations_mapping = {player: [] for player in trash_counts}
            for location in fill_locations:
                if 'Ganons Tower' in location.name and location.player in locations_mapping:
                    locations_mapping[location.player].append(location)

            for player, trash_count in trash_counts.items():
                gtower_locations = locations_mapping[player]
                world.random.shuffle(gtower_locations)
                localrest = localrestitempool[player]
                if localrest:
                    gt_item_pool = restitempool + localrest
                    world.random.shuffle(gt_item_pool)
                else:
                    gt_item_pool = restitempool.copy()

                while gtower_locations and gt_item_pool and trash_count > 0:
                    spot_to_fill = gtower_locations.pop()
                    item_to_place = gt_item_pool.pop()
                    if item_to_place in localrest:
                        localrest.remove(item_to_place)
                    else:
                        restitempool.remove(item_to_place)
                    world.push_item(spot_to_fill, item_to_place, False)
                    fill_locations.remove(spot_to_fill)  # very slow, unfortunately
                    trash_count -= 1


def get_same_seed(world, seed_def: tuple) -> str:
    seeds: typing.Dict[tuple, str] = getattr(world, "__named_seeds", {})
    if seed_def in seeds:
        return seeds[seed_def]
    seeds[seed_def] = str(world.random.randint(0, 2 ** 64))
    world.__named_seeds = seeds
    return seeds[seed_def]


class ALttPLogic(LogicMixin):
    def _lttp_has_key(self, item, player, count: int = 1):
        if self.world.logic[player] == 'nologic':
            return True
        if self.world.smallkey_shuffle[player] == smallkey_shuffle.option_universal:
            return self.can_buy_unlimited('Small Key (Universal)', player)
        return self.prog_items[item, player] >= count
