import random
import logging
import os
import threading
import typing

from BaseClasses import Item, CollectionState
from . import alttp_generate_basic
from .standard.sub_classes import ALttPDoorsItem
from .alttp_init.load_options import load_options
from ..AutoWorld import World, LogicMixin
from .options.standard import SmallkeyShuffle
from .legacy.item_data import as_dict_item_table, item_name_groups, item_table
from .memory_data.region_data import lookup_name_to_id, create_regions, mark_light_world_regions
from .legacy.rules.rules import set_rules
from .legacy.item_pool import generate_itempool, difficulties
from .legacy.shop_fill import create_shops, ShopSlotFill
from .legacy.dungeons import create_dungeons
from .legacy.rom import LocalRom, patch_rom, patch_race_rom, patch_enemizer, apply_rom_settings, get_hash_string, \
    get_base_rom_path
import Patch

from .legacy.inverted_regions import create_inverted_regions, mark_dark_world_regions
from .legacy.entrance_randomizer_shuffle import link_entrances, link_inverted_entrances, plando_connect

import worlds.alttp_doors.alttp_generate_early
import worlds.alttp_doors.alttp_create_regions
import worlds.alttp_doors.alttp_create_items
import worlds.alttp_doors.alttp_pre_fill

lttp_logger = logging.getLogger("A Link to the Past + Doors")



class ALTTPDoorsWorld(World):
    """
    The Legend of Zelda: A Link to the Past is an action/adventure game. Take on the role of
    Link, a boy who is destined to save the land of Hyrule. Delve through three palaces and nine
    dungeons on your quest to rescue the descendents of the seven wise men and defeat the evil
    Ganon!
    """
    game: str = "A Link to the Past + Doors"
    options = load_options()
    uses_local_game_settings = True

    topology_present = True
    item_name_groups = item_name_groups
    hint_blacklist = {"Triforce"}

    item_name_to_id = {name: data.item_code for name, data in item_table.items() if type(data.item_code) == int}
    location_name_to_id = lookup_name_to_id

    data_version = 9 # Acting as if moving from standard alttp
    remote_items: bool = False
    remote_start_inventory: bool = False


    def __init__(self, *args, **kwargs):
        self.dungeon_local_item_names = set()
        self.dungeon_specific_item_names = set()
        self.rom_name_available_event = threading.Event()
        self.has_progressive_bows = False
        super(ALTTPDoorsWorld, self).__init__(*args, **kwargs)

    def generate_early(self):
        player = self.player
        world = self.world

        # Used for the setup methods to store stuff
        self.metadata = {}

        alttp_generate_early.handle_assured_sword(self)
        alttp_generate_early.handle_vanilla_sword_placement(self)
        alttp_generate_early.handle_glitch_boots(self)
        alttp_generate_early.handle_random_starting_items(self)

        # # system for sharing ER layouts
        # self.er_seed = str(world.random.randint(0, 2 ** 64))
        #
        # if "-" in world.shuffle[player]:
        #     shuffle, seed = world.shuffle[player].split("-", 1)
        #     world.shuffle[player] = shuffle
        #     if shuffle == "vanilla":
        #         self.er_seed = "vanilla"
        #     elif seed.startswith("group-") or world.is_race:
        #         self.er_seed = get_same_seed(world, (
        #             shuffle, seed, world.retro[player], world.mode[player], world.logic[player]))
        #     else:  # not a race or group seed, use set seed as is.
        #         self.er_seed = seed
        # elif world.shuffle[player] == "vanilla":
        #     self.er_seed = "vanilla"
        # for dungeon_item in ["smallkey_shuffle", "bigkey_shuffle", "compass_shuffle", "map_shuffle"]:
        #     option = self.game_settings[dungeon_item]
        #     if option == "own_world":
        #         self.game_settings["local_items"].value |= self.item_name_groups[option.item_name_group]
        #     elif option == "different_world":
        #         self.game_settings["non_local_items"].value |= self.item_name_groups[option.item_name_group]
        #     elif option.in_dungeon:
        #         self.dungeon_local_item_names |= self.item_name_groups[option.item_name_group]
        #         if option == "original_dungeon":
        #             self.dungeon_specific_item_names |= self.item_name_groups[option.item_name_group]
        #
        # #world.difficulty_requirements[player] = difficulties[world.difficulty[player]]
        self.game_settings["difficulty_requirements"] = difficulties[world.difficulty[player]]

    def create_regions(self):
        player = self.player
        world = self.world

        #alttp_create_regions.handle_base_regions(self)
        alttp_create_regions.handle_pyramid_open(self)
        alttp_create_regions.handle_pot_shuffle(self)
        alttp_create_regions.handle_shop_main_pool_shuffle(self)
        alttp_create_regions.handle_hybrid_major_glitches_regions(self)


        # if self.game_settings["open_pyramid"] == 'goal':
        #     self.game_settings["open_pyramid"] = self.game_settings["goal"] in {'crystals', 'ganontriforcehunt',
        #                                                         'localganontriforcehunt', 'ganonpedestal'}
        # elif self.game_settings["open_pyramid"] == 'auto':
        #     self.game_settings["open_pyramid"] = self.game_settings["goal"] in {'crystals', 'ganontriforcehunt',
        #                                                         'localganontriforcehunt', 'ganonpedestal'} and \
        #                                  (self.game_settings["shuffle"] in {'vanilla', 'dungeonssimple', 'dungeonsfull',
        #                                                             'dungeonscrossed'} or not world.shuffle_ganon)
        # else:
        #     self.game_settings["open_pyramid"] = {'on': True, 'off': False, 'yes': True, 'no': False}.get(
        #         self.game_settings["open_pyramid"], 'auto')
        #
        # self.game_settings["triforce_pieces_available"] = max(self.game_settings["triforce_pieces_available"],
        #                                               self.game_settings["triforce_pieces_available"])

        if self.game_settings["world_state"] != 'inverted':
            create_regions(world, player)
        else:
            create_inverted_regions(world, player)
        create_shops(world, self, player)
        create_dungeons(world, self, player)

        l = []
        for r in world.regions:
            if r.player == player:
                l += r.locations

        self.metadata["locations"] = l

        if self.game_settings["logic"] not in ["no_glitches", "minor_glitches"] and self.game_settings["shuffle"] in \
                {"vanilla", "dungeons_simple", "dungeons_full", "simple", "restricted", "full"}:
            world.fix_fake_world[player] = False

        # seeded entrance shuffle
        old_random = world.random
        #world.random = random.Random(self.er_seed)

        if self.game_settings["world_state"] != 'inverted':
            link_entrances(world, player)
            mark_light_world_regions(world, player)
        else:
            link_inverted_entrances(world, player)
            mark_dark_world_regions(world, player)

        world.random = old_random
        plando_connect(world, player)

    def set_rules(self):
        # TODO - add rules lel
        #set_rules(self)
        pass

    def generate_basic(self):
        alttp_generate_basic.randomize_region_entrances(self)

    def create_items(self):
        #generate_itempool(self)
        # A dict of items that should be in the pool
        self.item_pool = {}

        # Add the vanilla items to the pool
        alttp_create_items.create_vanilla_pool(self)


        alttp_create_items.handle_progressive(self)
        alttp_create_items.handle_difficulty(self)
        alttp_create_items.handle_swords(self)
        alttp_create_items.handle_timed_clocks(self)
        alttp_create_items.handle_capacity_upgrades(self)
        alttp_create_items.handle_shops(self)
        alttp_create_items.handle_retro_mode(self)


        alttp_create_items.handle_key_drop_shuffle(self)
        alttp_create_items.handle_triforce_hunt(self)
        alttp_create_items.handle_custom_pool(self)
        alttp_create_items.handle_item_groups(self)


        # When to do junk and bees?
        alttp_create_items.handle_junk(self)
        alttp_create_items.handle_beemizer(self)

        # TODO: Ganon special bow? (alt)


        created_items = []
        for k in self.item_pool:
            for n in range(self.item_pool[k]):
                created_items.append(self.create_item(k))

        self.world.itempool += created_items



    def modify_multidata(self, multidata: dict):
        """For deeper modification of server multidata."""
        pass

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
                    elif state.has('Tempered Sword', item.player) and self.game_settings["difficulty_requirements"].progressive_sword_limit >= 4:
                        return 'Golden Sword'
                    elif state.has('Master Sword', item.player) and self.game_settings["difficulty_requirements"].progressive_sword_limit >= 3:
                        return 'Tempered Sword'
                    elif state.has('Fighter Sword', item.player) and self.game_settings["difficulty_requirements"].progressive_sword_limit >= 2:
                        return 'Master Sword'
                    elif self.game_settings["difficulty_requirements"].progressive_sword_limit >= 1:
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
                    elif state.has('Red Shield', item.player) and self.game_settings["difficulty_requirements"].progressive_shield_limit >= 3:
                        return 'Mirror Shield'
                    elif state.has('Blue Shield', item.player)  and self.game_settings["difficulty_requirements"].progressive_shield_limit >= 2:
                        return 'Red Shield'
                    elif self.game_settings["difficulty_requirements"].progressive_shield_limit >= 1:
                        return 'Blue Shield'
                elif 'Bow' in item_name:
                    if state.has('Silver Bow', item.player):
                        return
                    elif state.has('Bow', item.player) and (self.game_settings["difficulty_requirements"].progressive_bow_limit >= 2
                        or self.world.logic[item.player] == 'noglitches'
                        or self.world.swordless[item.player]): # modes where silver bow is always required for ganon
                        return 'Silver Bow'
                    elif self.game_settings["difficulty_requirements"].progressive_bow_limit >= 1:
                        return 'Bow'
        elif item.advancement:
            return item_name

    def pre_fill(self):

        # Agahnim, frog, etc.
        alttp_pre_fill.handle_events(self)
        # Find some spots for crystals #TODO - allow the algorithm to generate these? THey were preplaced before tho so idk
        alttp_pre_fill.handle_crystals(self)
        # Place the Triforce where it belongs
        alttp_pre_fill.handle_triforce_placement(self)

        n = self.metadata['locations'].__len__()
        for l in self.metadata['locations']:
            if l.item is not None:
                n -= 1
                print(f"{l} has item {l.item} after item stage")
        print(f"Player {self.player} has {n} open locations remaining after pre-fill")


    @classmethod
    def stage_pre_fill(cls, world):
        pass
        # from .legacy.dungeons import fill_dungeons_restrictive
        # fill_dungeons_restrictive(cls, world)

    @classmethod
    def stage_post_fill(cls, world):
        pass
        # ShopSlotFill(world)

    def generate_output(self, output_directory: str):
        world = self.world
        player = self.player
        try:
            use_enemizer = (self.game_settings["boss_shuffle"] != 'none' or self.game_settings["enemy_shuffle"]
                            or self.game_settings["enemy_health"] != 'default' or self.game_settings["enemy_damage"] != 'default'
                            or self.game_settings["pot_location_shuffle"] or self.game_settings["bush_shuffle"]
                            or self.game_settings["killable_thieves"])

            rom = LocalRom(get_base_rom_path())

            patch_rom(world, rom, player, use_enemizer)

            if use_enemizer:
                patch_enemizer(world, player, rom, world.enemizer, output_directory)

            if world.is_race:
                patch_race_rom(rom, world, player)

            world.spoiler.hashes[player] = get_hash_string(rom.hash)

            palettes_options = {
                'dungeon': self.game_settings["uw_palettes"],
                'overworld': self.game_settings["ow_palettes"],
                'hud': self.game_settings["hud_palettes"],
                'sword': self.game_settings["sword_palettes"],
                'shield': self.game_settings["shield_palettes"],
                'link': self.game_settings["link_palettes"],
            }
            palettes_options = {key: option.current_key for key, option in palettes_options.items()}

            apply_rom_settings(rom, self.game_settings["heartbeep"].current_key,
                               self.game_settings["heartcolor"].current_key,
                               self.game_settings["quickswap"],
                               self.game_settings["menuspeed"].current_key,
                               self.game_settings["music"],
                               self.game_settings["sprite"],
                               palettes_options, world, player, True,
                               reduceflashing=self.game_settings["reduceflashing"] or world.is_race,
                               triforcehud=self.game_settings["triforcehud"].current_key)

            outfilepname = f'_P{player}'
            outfilepname += f"_{world.player_name[player].replace(' ', '_')}" \
                if world.player_name[player] != 'Player%d' % player else ''

            rompath = os.path.join(output_directory, f'AP_{world.seed_name}{outfilepname}.sfc')
            rom.write_to_file(rompath)
            Patch.create_patch_file(rompath, player=player, player_name=world.player_name[player])
            os.unlink(rompath)
            self.rom_name = rom.name
        except:
            raise
        finally:
            self.rom_name_available_event.set() # make sure threading continues and errors are collected

    def modify_multidata(self, multidata: dict):
        # This exists for client support
        multidata["games"][self.player] = "A Link to the Past"
        import base64
        # wait for self.rom_name to be available.
        self.rom_name_available_event.wait()
        rom_name = getattr(self, "rom_name", None)
        # we skip in case of error, so that the original error in the output thread is the one that gets raised
        if rom_name:
            new_name = base64.b64encode(bytes(self.rom_name)).decode()
            payload = multidata["connect_names"][self.world.player_name[self.player]]
            multidata["connect_names"][new_name] = payload
            del (multidata["connect_names"][self.world.player_name[self.player]])

    def get_required_client_version(self) -> tuple:
        return max((0, 1, 4), super(ALTTPDoorsWorld, self).get_required_client_version())

    def create_item(self, name: str) -> Item:
        return ALttPDoorsItem(name, self.player, **as_dict_item_table[name])

    @classmethod
    def stage_fill_hook(cls, world, progitempool, nonexcludeditempool, localrestitempool, nonlocalrestitempool,
                        restitempool, fill_locations):
        trash_counts = {}
        standard_keyshuffle_players = set()
        for player in world.get_game_players("A Link to the Past"):
            if world.mode[player] == 'standard' and world.SmallkeyShuffle[player] \
                    and world.SmallkeyShuffle[player] != SmallkeyShuffle.option_universal:
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
    def _lttp_doors_has_key(self, item, player, count: int = 1):
        if self.world.worlds[player].game_settings["logic"] == 'nologic':
            return True
        if self.world.worlds[player].game_settings["smallkey_shuffle"] == SmallkeyShuffle.option_universal:
            return self.can_buy_unlimited('Small Key (Universal)', player)
        return self.prog_items[item, player] >= count
