"""Module to choose game weights provided in a YAML"""
import argparse
import logging
import random
import typing
import urllib

import Options
from Utils import tuplize_version, version_tuple, __version__, parse_yaml
from worlds import AutoWorldRegister


# ------------------ #
# Value roll methods #
# ------------------ #


def roll_settings(weights: dict, logger: logging.Logger, plando_options: typing.Set[str] = frozenset(("bosses",))):
    """Decide all of the settings that will be used for world generation"""
    if "linked_options" in weights:
        weights = roll_linked_options(weights)

    if "triggers" in weights:
        weights = roll_triggers(weights, weights["triggers"])

    requirements = weights.get("requires", {})
    if requirements:
        version = requirements.get("version", __version__)
        if tuplize_version(version) > version_tuple:
            raise Exception(f"Settings reports required version of generator is at least {version}, "
                            f"however generator is of version {__version__}")
        required_plando_options = requirements.get("plando", "")
        if required_plando_options:
            required_plando_options = set(option.strip() for option in required_plando_options.split(","))
            required_plando_options -= plando_options
            if required_plando_options:
                if len(required_plando_options) == 1:
                    raise Exception(
                        f"Settings reports required plando module {', '.join(required_plando_options)}, "
                        f"which is not enabled.")
                else:
                    raise Exception(
                        f"Settings reports required plando modules {', '.join(required_plando_options)}, "
                        f"which are not enabled.")

    ret = argparse.Namespace()
    for option_key in Options.per_game_common_options:
        if option_key in weights:
            raise Exception(f"Option {option_key} has to be in a game's section, not on its own.")

    ret.game = get_choice("game", weights)
    if ret.game not in weights:
        raise Exception(f"No game options for selected game \"{ret.game}\" found.")

    world_type = AutoWorldRegister.world_types[ret.game]
    game_weights = weights[ret.game]

    if "triggers" in game_weights:
        weights = roll_triggers(weights, game_weights["triggers"])
        game_weights = weights[ret.game]

    ret.name = get_choice('name', weights)
    for option_key, option in Options.common_options.items():
        setattr(ret, option_key, option.from_any(get_choice(option_key, weights, option.default)))

    if ret.game in AutoWorldRegister.world_types:
        for option_key, option in world_type.options.items():
            handle_option(ret, game_weights, option_key, option)
        for option_key, option in Options.per_game_common_options.items():
            handle_option(ret, game_weights, option_key, option)
        # Item plando
        if "items" in plando_options:
            ret.plando_items = roll_item_plando(world_type, game_weights)
        if ret.game == "Minecraft":
            # bad hardcoded behavior to make this work for now
            ret.plando_connections = []
            if "connections" in plando_options:
                options = game_weights.get("plando_connections", [])
                for placement in options:
                    if roll_percentage(get_choice("percentage", placement, 100)):
                        ret.plando_connections.append(PlandoConnection(
                            get_choice("entrance", placement),
                            get_choice("exit", placement),
                            get_choice("direction", placement, "both")
                        ))
        elif ret.game == "A Link to the Past":
            pass
            # TODO: Remove this check entirely
            # raise Exception("This should not be needed with the new options system!")
            # roll_alttp_settings(ret, game_weights, plando_options, logger)
    else:
        raise Exception(f"Unsupported game {ret.game}")
    return ret


def roll_item_plando(world_type, weights):
    """Choose and validate the existence of plando'd items and their locations"""
    plando_items = []

    def add_plando_item(item: str, location: str):
        """Parse the item/location to be plando'd"""
        if item not in world_type.item_name_to_id:
            raise Exception(f"Could not plando item {item} as the item was not recognized")
        if location not in world_type.location_name_to_id:
            raise Exception(
                f"Could not plando item {item} at location {location} as the location was not recognized")
        plando_items.append(PlandoItem(item, location, location_world, from_pool, force))

    options = weights.get("plando_items", [])
    for placement in options:
        if roll_percentage(get_choice_legacy("percentage", placement, 100)):
            from_pool = get_choice_legacy("from_pool", placement, PlandoItem._field_defaults["from_pool"])
            location_world = get_choice_legacy("world", placement, PlandoItem._field_defaults["world"])
            force = str(get_choice_legacy("force", placement, PlandoItem._field_defaults["force"])).lower()
            if "items" in placement and "locations" in placement:
                items = placement["items"]
                locations = placement["locations"]
                if isinstance(items, dict):
                    item_list = []
                    for key, value in items.items():
                        item_list += [key] * value
                    items = item_list
                if not items or not locations:
                    raise Exception("You must specify at least one item and one location to place items.")
                random.shuffle(items)
                random.shuffle(locations)
                for item, location in zip(items, locations):
                    add_plando_item(item, location)
            else:
                item = get_choice_legacy("item", placement, get_choice_legacy("items", placement))
                location = get_choice_legacy("location", placement)
                add_plando_item(item, location)
    return plando_items


def roll_linked_options(weights: dict, logger: logging.Logger) -> dict:
    weights = weights.copy()  # make sure we don't write back to other weights sets in same_settings
    for option_set in weights["linked_options"]:
        if "name" not in option_set:
            raise ValueError("One of your linked options does not have a name.")
        try:
            if roll_percentage(option_set["percentage"]):
                logger.debug(f"Linked option {option_set['name']} triggered.")
                new_options = option_set["options"]
                for category_name, category_options in new_options.items():
                    currently_targeted_weights = weights
                    if category_name:
                        currently_targeted_weights = currently_targeted_weights[category_name]
                    update_weights(currently_targeted_weights, category_options, "Linked", option_set["name"])
            else:
                logger.debug(f"linked option {option_set['name']} skipped.")
        except Exception as e:
            raise ValueError(f"Linked option {option_set['name']} is destroyed. "
                             f"Please fix your linked option.") from e
    return weights


def roll_triggers(weights: dict, triggers: list, logger: logging.Logger) -> dict:
    weights = weights.copy()  # make sure we don't write back to other weights sets in same_settings
    weights["_Generator_Version"] = "Archipelago"  # Some means for triggers to know if the seed is on main or doors.
    for i, option_set in enumerate(triggers):
        try:
            currently_targeted_weights = weights
            category = option_set.get("option_category", None)
            if category:
                currently_targeted_weights = currently_targeted_weights[category]
            key = get_choice("option_name", option_set)
            if key not in currently_targeted_weights:
                logger.warning(f'Specified option name {option_set["option_name"]} did not '
                                f'match with a root option. '
                                f'This is probably in error.')
            trigger_result = get_choice("option_result", option_set)
            result = get_choice(key, currently_targeted_weights)
            currently_targeted_weights[key] = result
            if result == trigger_result and roll_percentage(get_choice("percentage", option_set, 100)):
                for category_name, category_options in option_set["options"].items():
                    currently_targeted_weights = weights
                    if category_name:
                        currently_targeted_weights = currently_targeted_weights[category_name]
                    update_weights(currently_targeted_weights, category_options, "Triggered", option_set["option_name"])

        except Exception as e:
            raise ValueError(f"Your trigger number {i + 1} is destroyed. "
                             f"Please fix your triggers.") from e
    return weights


def roll_percentage(percentage: typing.Union[int, float]) -> bool:
    """Roll a percentage chance.
    percentage is expected to be in range [0, 100]"""
    return random.random() < (float(percentage) / 100)


# -------------- #
# Helper methods #
# -------------- #

def handle_option(ret: argparse.Namespace, game_weights: dict, option_key: str, option: type(Options.Option)):
    """Select the option's value, based on weights if applicable, and add the chosen attribute:value pair to ret"""
    if option_key in game_weights:
        try:
            if not option.supports_weighting:
                player_option = option.from_any(game_weights[option_key])
            else:
                player_option = option.from_any(get_choice(option_key, game_weights))
            setattr(ret, option_key, player_option)
        except Exception as e:
            raise Exception(f"Error generating option {option_key} in {ret.game}") from e
        else:
            # verify item names existing
            if getattr(player_option, "verify_item_name", False):
                for item_name in player_option.value:
                    if item_name not in AutoWorldRegister.world_types[ret.game].item_names:
                        raise Exception(f"Item {item_name} from option {player_option} "
                                        f"is not a valid item name from {ret.game}")
            elif getattr(player_option, "verify_location_name", False):
                for location_name in player_option.value:
                    if location_name not in AutoWorldRegister.world_types[ret.game].location_names:
                        raise Exception(f"Location {location_name} from option {player_option} "
                                        f"is not a valid location name from {ret.game}")
    else:
        setattr(ret, option_key, option(option.default))


def interpret_on_off(value):
    return {"on": True, "off": False}.get(value, value)


def convert_to_on_off(value):
    return {True: "on", False: "off"}.get(value, value)


def get_choice_legacy(option, root, value=None) -> typing.Any:
    if option not in root:
        return value
    if type(root[option]) is list:
        return interpret_on_off(random.choices(root[option])[0])
    if type(root[option]) is not dict:
        return interpret_on_off(root[option])
    if not root[option]:
        return value
    if any(root[option].values()):
        return interpret_on_off(
            random.choices(list(root[option].keys()), weights=list(map(int, root[option].values())))[0])
    raise RuntimeError(f"All options specified in \"{option}\" are weighted as zero.")


def get_choice(option, root, value=None) -> typing.Any:
    """Randomly assign the given option a value based on the provided weights"""
    if option not in root:
        return value
    if type(root[option]) is list:
        return random.choices(root[option])[0]
    if type(root[option]) is not dict:
        return root[option]
    if not root[option]:
        return value
    if any(root[option].values()):
        return random.choices(list(root[option].keys()), weights=list(map(int, root[option].values())))[0]
    raise RuntimeError(f"All options specified in \"{option}\" are weighted as zero.")


def read_weights_yaml(path):
    try:
        if urllib.parse.urlparse(path).scheme:
            yaml = str(urllib.request.urlopen(path).read(), "utf-8")
        else:
            with open(path, 'rb') as f:
                yaml = str(f.read(), "utf-8")
    except Exception as e:
        raise Exception(f"Failed to read weights ({path})") from e

    return parse_yaml(yaml)


def update_weights(weights: dict, new_weights: dict, type: str, name: str, logger: logging.Logger) -> dict:
    logger.debug(f'Applying {new_weights}')
    new_options = set(new_weights) - set(weights)
    weights.update(new_weights)
    if new_options:
        for new_option in new_options:
            logger.warning(f'{type} Suboption "{new_option}" of "{name}" did not '
                            f'overwrite a root option. '
                            f'This is probably in error.')
    return weights

# ----------------------- #
# aLttP legacy - removing #
# ----------------------- #

from worlds.alttp_legacy import Options as LttPOptions, Bosses
from worlds.alttp_legacy.Text import TextTable
from worlds.generic import PlandoConnection, PlandoItem

available_boss_names: typing.Set[str] = {boss.lower() for boss in Bosses.boss_table if boss not in
                                         {'Agahnim', 'Agahnim2', 'Ganon'}}

available_boss_locations: typing.Set[str] = {f"{loc.lower()}{f' {level}' if level else ''}" for loc, level in
                                             Bosses.boss_location_table}

boss_shuffle_options = {None: 'none',
                        'none': 'none',
                        'basic': 'basic',
                        'full': 'full',
                        'chaos': 'chaos',
                        'singularity': 'singularity'
                        }

goals = {
    'ganon': 'ganon',
    'crystals': 'crystals',
    'bosses': 'bosses',
    'pedestal': 'pedestal',
    'ganon_pedestal': 'ganonpedestal',
    'triforce_hunt': 'triforcehunt',
    'local_triforce_hunt': 'localtriforcehunt',
    'ganon_triforce_hunt': 'ganontriforcehunt',
    'local_ganon_triforce_hunt': 'localganontriforcehunt',
    'ice_rod_hunt': 'icerodhunt',
}


def get_plando_bosses(boss_shuffle: str, plando_options: typing.Set[str]) -> str:
    if boss_shuffle in boss_shuffle_options:
        return boss_shuffle_options[boss_shuffle]
    elif "bosses" in plando_options:
        options = boss_shuffle.lower().split(";")
        remainder_shuffle = "none"  # vanilla
        bosses = []
        for boss in options:
            if boss in boss_shuffle_options:
                remainder_shuffle = boss_shuffle_options[boss]
            elif "-" in boss:
                loc, boss_name = boss.split("-")
                if boss_name not in available_boss_names:
                    raise ValueError(f"Unknown Boss name {boss_name}")
                if loc not in available_boss_locations:
                    raise ValueError(f"Unknown Boss Location {loc}")
                level = ''
                if loc.split(" ")[-1] in {"top", "middle", "bottom"}:
                    # split off level
                    loc = loc.split(" ")
                    level = f" {loc[-1]}"
                    loc = " ".join(loc[:-1])
                loc = loc.title().replace("Of", "of")
                if not Bosses.can_place_boss(boss_name.title(), loc, level):
                    raise ValueError(f"Cannot place {boss_name} at {loc}{level}")
                bosses.append(boss)
            elif boss not in available_boss_names:
                raise ValueError(f"Unknown Boss name or Boss shuffle option {boss}.")
            else:
                bosses.append(boss)
        return ";".join(bosses + [remainder_shuffle])
    else:
        raise Exception(f"Boss Shuffle {boss_shuffle} is unknown and boss plando is turned off.")


def roll_alttp_settings(ret: argparse.Namespace, weights, plando_options, logger: logging.Logger):
    """Set aLttP specific options"""
    if "dungeon_items" in weights and get_choice_legacy('dungeon_items', weights, "none") != "none":
        raise Exception(f"dungeon_items key in A Link to the Past was removed, but is present in these weights as {get_choice_legacy('dungeon_items', weights, False)}.")
    glitches_required = get_choice_legacy('glitches_required', weights)
    if glitches_required not in [None, 'none', 'no_logic', 'overworld_glitches', 'hybrid_major_glitches', 'minor_glitches']:
        logger.warning("Only NMG, OWG, HMG and No Logic supported")
        glitches_required = 'none'
    ret.logic = {None: 'noglitches', 'none': 'noglitches', 'no_logic': 'nologic', 'overworld_glitches': 'owglitches',
                 'minor_glitches': 'minorglitches', 'hybrid_major_glitches': 'hybridglitches'}[
        glitches_required]

    ret.dark_room_logic = get_choice_legacy("dark_room_logic", weights, "lamp")
    if not ret.dark_room_logic:  # None/False
        ret.dark_room_logic = "none"
    if ret.dark_room_logic == "sconces":
        ret.dark_room_logic = "torches"
    if ret.dark_room_logic not in {"lamp", "torches", "none"}:
        raise ValueError(f"Unknown Dark Room Logic: \"{ret.dark_room_logic}\"")

    entrance_shuffle = get_choice_legacy('entrance_shuffle', weights, 'vanilla')
    if entrance_shuffle.startswith('none-'):
        ret.shuffle = 'vanilla'
    else:
        ret.shuffle = entrance_shuffle if entrance_shuffle != 'none' else 'vanilla'

    goal = get_choice_legacy('goals', weights, 'ganon')

    ret.goal = goals[goal]

    # TODO consider moving open_pyramid to an automatic variable in the core roller, set to True when
    # fast ganon + ganon at hole
    ret.open_pyramid = get_choice_legacy('open_pyramid', weights, 'goal')

    extra_pieces = get_choice_legacy('triforce_pieces_mode', weights, 'available')

    ret.triforce_pieces_required = LttPOptions.TriforcePieces.from_any(get_choice_legacy('triforce_pieces_required', weights, 20))

    # sum a percentage to required
    if extra_pieces == 'percentage':
        percentage = max(100, float(get_choice_legacy('triforce_pieces_percentage', weights, 150))) / 100
        ret.triforce_pieces_available = int(round(ret.triforce_pieces_required * percentage, 0))
    # vanilla mode (specify how many pieces are)
    elif extra_pieces == 'available':
        ret.triforce_pieces_available = LttPOptions.TriforcePieces.from_any(
            get_choice_legacy('triforce_pieces_available', weights, 30))
    # required pieces + fixed extra
    elif extra_pieces == 'extra':
        extra_pieces = max(0, int(get_choice_legacy('triforce_pieces_extra', weights, 10)))
        ret.triforce_pieces_available = ret.triforce_pieces_required + extra_pieces

    # change minimum to required pieces to avoid problems
    # also cap max pieces at 90
    ret.triforce_pieces_available = min(max(ret.triforce_pieces_required, int(ret.triforce_pieces_available)), 90)

    ret.shop_shuffle = get_choice_legacy('shop_shuffle', weights, '')
    if not ret.shop_shuffle:
        ret.shop_shuffle = ''

    ret.mode = get_choice_legacy("mode", weights)

    ret.difficulty = get_choice_legacy('item_pool', weights)

    ret.item_functionality = get_choice_legacy('item_functionality', weights)

    boss_shuffle = get_choice_legacy('boss_shuffle', weights)
    ret.shufflebosses = get_plando_bosses(boss_shuffle, plando_options)

    ret.enemy_damage = {None: 'default',
                        'default': 'default',
                        'shuffled': 'shuffled',
                        'random': 'chaos', # to be removed
                        'chaos': 'chaos',
                        }[get_choice_legacy('enemy_damage', weights)]

    ret.enemy_health = get_choice_legacy('enemy_health', weights)

    ret.beemizer = int(get_choice_legacy('beemizer', weights, 0))

    ret.timer = {'none': False,
                 None: False,
                 False: False,
                 'timed': 'timed',
                 'timed_ohko': 'timed-ohko',
                 'ohko': 'ohko',
                 'timed_countdown': 'timed-countdown',
                 'display': 'display'}[get_choice_legacy('timer', weights, False)]

    ret.countdown_start_time = int(get_choice_legacy('countdown_start_time', weights, 10))
    ret.red_clock_time = int(get_choice_legacy('red_clock_time', weights, -2))
    ret.blue_clock_time = int(get_choice_legacy('blue_clock_time', weights, 2))
    ret.green_clock_time = int(get_choice_legacy('green_clock_time', weights, 4))

    ret.dungeon_counters = get_choice_legacy('dungeon_counters', weights, 'default')

    ret.shuffle_prizes = get_choice_legacy('shuffle_prizes', weights, "g")

    ret.required_medallions = [get_choice_legacy("misery_mire_medallion", weights, "random"),
                               get_choice_legacy("turtle_rock_medallion", weights, "random")]

    for index, medallion in enumerate(ret.required_medallions):
        ret.required_medallions[index] = {"ether": "Ether", "quake": "Quake", "bombos": "Bombos", "random": "random"} \
            .get(medallion.lower(), None)
        if not ret.required_medallions[index]:
            raise Exception(f"unknown Medallion {medallion} for {'misery mire' if index == 0 else 'turtle rock'}")

    ret.plando_texts = {}
    if "texts" in plando_options:
        tt = TextTable()
        tt.removeUnwantedText()
        options = weights.get("plando_texts", [])
        for placement in options:
            if roll_percentage(get_choice_legacy("percentage", placement, 100)):
                at = str(get_choice_legacy("at", placement))
                if at not in tt:
                    raise Exception(f"No text target \"{at}\" found.")
                ret.plando_texts[at] = str(get_choice_legacy("text", placement))

    ret.plando_connections = []
    if "connections" in plando_options:
        options = weights.get("plando_connections", [])
        for placement in options:
            if roll_percentage(get_choice_legacy("percentage", placement, 100)):
                ret.plando_connections.append(PlandoConnection(
                    get_choice_legacy("entrance", placement),
                    get_choice_legacy("exit", placement),
                    get_choice_legacy("direction", placement, "both")
                ))

    ret.sprite_pool = weights.get('sprite_pool', [])
    ret.sprite = get_choice_legacy('sprite', weights, "Link")
    if 'random_sprite_on_event' in weights:
        randomoneventweights = weights['random_sprite_on_event']
        if get_choice_legacy('enabled', randomoneventweights, False):
            ret.sprite = 'randomon'
            ret.sprite += '-hit' if get_choice_legacy('on_hit', randomoneventweights, True) else ''
            ret.sprite += '-enter' if get_choice_legacy('on_enter', randomoneventweights, False) else ''
            ret.sprite += '-exit' if get_choice_legacy('on_exit', randomoneventweights, False) else ''
            ret.sprite += '-slash' if get_choice_legacy('on_slash', randomoneventweights, False) else ''
            ret.sprite += '-item' if get_choice_legacy('on_item', randomoneventweights, False) else ''
            ret.sprite += '-bonk' if get_choice_legacy('on_bonk', randomoneventweights, False) else ''
            ret.sprite = 'randomonall' if get_choice_legacy('on_everything', randomoneventweights, False) else ret.sprite
            ret.sprite = 'randomonnone' if ret.sprite == 'randomon' else ret.sprite

            if (not ret.sprite_pool or get_choice_legacy('use_weighted_sprite_pool', randomoneventweights, False)) \
                    and 'sprite' in weights:  # Use sprite as a weighted sprite pool, if a sprite pool is not already defined.
                for key, value in weights['sprite'].items():
                    if key.startswith('random'):
                        ret.sprite_pool += ['random'] * int(value)
                    else:
                        ret.sprite_pool += [key] * int(value)

