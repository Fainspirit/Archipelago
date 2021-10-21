import argparse
import logging
import random
import urllib.request
import urllib.parse
import typing
import os
from collections import Counter
import string

import ModuleUpdate
from yaml_tools import get_choice, roll_settings, read_weights_yaml

ModuleUpdate.update()

from worlds.generic import PlandoItem, PlandoConnection
from Utils import parse_yaml, get_options
from worlds.alttp_legacy.EntranceRandomizer import parse_arguments
from Main import main as ERmain
from BaseClasses import seeddigits, get_seed
import Options
from worlds.alttp_legacy import Bosses
from worlds.alttp_legacy.Text import TextTable
from worlds.AutoWorld import AutoWorldRegister


categories = set(AutoWorldRegister.world_types)

def parse_multiworld_args():
    options = get_options()
    defaults = options["generator"]

    parser = argparse.ArgumentParser(description="CMD Generation Interface, defaults come from host.yaml.")
    parser.add_argument('--weights_file_path', default = defaults["weights_file_path"],
                        help='Path to the weights file to use for rolling game settings, urls are also valid')
    parser.add_argument('--samesettings', help='Rolls settings per weights file rather than per player',
                        action='store_true')
    parser.add_argument('--player_files_path', default=defaults["player_files_path"],
                        help="Input directory for player files.")
    parser.add_argument('--seed', help='Define seed number to generate.', type=int)
    parser.add_argument('--multi', default=defaults["players"], type=lambda value: max(int(value), 1))
    parser.add_argument('--spoiler', type=int, default=defaults["spoiler"])
    parser.add_argument('--rom', default=options["lttp_options"]["rom_file"], help="Path to the 1.0 JP LttP Baserom.")
    parser.add_argument('--enemizercli', default=defaults["enemizer_path"])
    parser.add_argument('--outputpath', default=options["general_options"]["output_path"])
    parser.add_argument('--race', action='store_true', default=defaults["race"])
    parser.add_argument('--meta_file_path', default=defaults["meta_file_path"])
    parser.add_argument('--log_output_path', help='Path to store output log')
    parser.add_argument('--log_level', default='info', help='Sets log level')
    parser.add_argument('--yaml_output', default=0, type=lambda value: max(int(value), 0),
                        help='Output rolled mystery results to yaml up to specified number (made for async multiworld)')
    parser.add_argument('--plando', default=defaults["plando_options"],
                        help='List of options that can be set manually. Can be combined, for example "bosses, items"')
    args = parser.parse_args()
    if not os.path.isabs(args.weights_file_path):
        args.weights_file_path = os.path.join(args.player_files_path, args.weights_file_path)
    if not os.path.isabs(args.meta_file_path):
        args.meta_file_path = os.path.join(args.player_files_path, args.meta_file_path)
    args.plando: typing.Set[str] = {arg.strip().lower() for arg in args.plando.split(",")}
    return args, options


def get_seed_name(random):
    return f"{random.randint(0, pow(10, seeddigits) - 1)}".zfill(seeddigits)


def main(args=None, callback=ERmain):
    if not args:
        args, options = parse_multiworld_args()

    seed = get_seed(args.seed)
    random.seed(seed)
    seed_name = get_seed_name(random)

    if args.race:
        random.seed()  # reset to time-based random source

    weights_cache = {}
    if args.weights_file_path and os.path.exists(args.weights_file_path):
        try:
            weights_cache[args.weights_file_path] = read_weights_yaml(args.weights_file_path)
        except Exception as e:
            raise ValueError(f"File {args.weights_file_path} is destroyed. Please fix your yaml.") from e
        print(f"Weights: {args.weights_file_path} >> "
              f"{get_choice('description', weights_cache[args.weights_file_path], 'No description specified')}")

    if args.meta_file_path and os.path.exists(args.meta_file_path):
        try:
            weights_cache[args.meta_file_path] = read_weights_yaml(args.meta_file_path)
        except Exception as e:
            raise ValueError(f"File {args.meta_file_path} is destroyed. Please fix your yaml.") from e
        meta_weights = weights_cache[args.meta_file_path]
        print(f"Meta: {args.meta_file_path} >> {get_choice('meta_description', meta_weights, 'No description specified')}")
        if args.samesettings:
            raise Exception("Cannot mix --samesettings with --meta")
    else:
        meta_weights = None
    player_id = 1
    player_files = {}
    for file in os.scandir(args.player_files_path):
        fname = file.name
        if file.is_file() and os.path.join(args.player_files_path, fname) not in {args.meta_file_path, args.weights_file_path}:
            path = os.path.join(args.player_files_path, fname)
            try:
                weights_cache[fname] = read_weights_yaml(path)
            except Exception as e:
                raise ValueError(f"File {fname} is destroyed. Please fix your yaml.") from e
            else:
                print(f"P{player_id} Weights: {fname} >> "
                      f"{get_choice('description', weights_cache[fname], 'No description specified')}")
                player_files[player_id] = fname
                player_id += 1

    args.multi = max(player_id-1, args.multi)
    print(f"Generating for {args.multi} player{'s' if args.multi > 1 else ''}, {seed_name} Seed {seed} with plando: "
          f"{', '.join(args.plando)}")

    if not weights_cache:
        raise Exception(f"No weights found. Provide a general weights file ({args.weights_file_path}) or individual player files. "
                        f"A mix is also permitted.")
    erargs = parse_arguments(['--multi', str(args.multi)])
    erargs.seed = seed
    erargs.glitch_triforce = options["generator"]["glitch_triforce_room"]
    erargs.spoiler = args.spoiler
    erargs.race = args.race
    erargs.outputname = seed_name
    erargs.outputpath = args.outputpath


    erargs.rom = args.rom
    erargs.enemizercli = args.enemizercli

    settings_cache = {k: (roll_settings(v, args.plando) if args.samesettings else None)
                      for k, v in weights_cache.items()}
    player_path_cache = {}
    for player in range(1, args.multi + 1):
        player_path_cache[player] = player_files.get(player, args.weights_file_path)

    if meta_weights:
        for player, path in player_path_cache.items():
            weights_cache[path].setdefault("meta_ignore", [])
        for key in meta_weights:
            option = get_choice(key, meta_weights)
            if option is not None:
                for player, path in player_path_cache.items():
                    players_meta = weights_cache[path].get("meta_ignore", [])
                    if key not in players_meta:
                        weights_cache[path][key] = option
                    elif type(players_meta) == dict and players_meta[key] and option not in players_meta[key]:
                        weights_cache[path][key] = option

    name_counter = Counter()
    erargs.player_settings = {}
    for player in range(1, args.multi + 1):
        path = player_path_cache[player]
        if path:
            try:
                # Calculate the final values for generation options
                settings = settings_cache[path] if settings_cache[path] else \
                    roll_settings(weights_cache[path], args.plando)
                # For each option, copy it to entrance randomizer args, overwriting existing values
                for k, v in vars(settings).items():
                    if v is not None:
                        try:
                            getattr(erargs, k)[player] = v
                        except AttributeError:
                            setattr(erargs, k, {player: v})
                        except Exception as e:
                            raise Exception(f"Error setting {k} to {v} for player {player}") from e
            except Exception as e:
                raise ValueError(f"File {path} is destroyed. Please fix your yaml.") from e
        else:
            raise RuntimeError(f'No weights specified for player {player}')
        if path == args.weights_file_path:  # if name came from the weights file, just use base player name
            erargs.name[player] = f"Player{player}"
        elif not erargs.name[player]:  # if name was not specified, generate it from filename
            erargs.name[player] = os.path.splitext(os.path.split(path)[-1])[0]
        # Set final player name
        erargs.name[player] = handle_name(erargs.name[player], player, name_counter)

    if len(set(erargs.name.values())) != len(erargs.name):
        raise Exception(f"Names have to be unique. Names: {erargs.name}")

    if args.yaml_output:
        import yaml
        important = {}
        for option, player_settings in vars(erargs).items():
            if type(player_settings) == dict:
                if all(type(value) != list for value in player_settings.values()):
                    if len(player_settings.values()) > 1:
                        important[option] = {player: value for player, value in player_settings.items() if
                                             player <= args.yaml_output}
                    elif len(player_settings.values()) > 0:
                        important[option] = player_settings[1]
                    else:
                        logging.debug(f"No player settings defined for option '{option}'")

            else:
                if player_settings != "":  # is not empty name
                    important[option] = player_settings
                else:
                    logging.debug(f"No player settings defined for option '{option}'")
        if args.outputpath:
            os.makedirs(args.outputpath, exist_ok=True)
        with open(os.path.join(args.outputpath if args.outputpath else ".", f"generate_{seed_name}.yaml"), "wt") as f:
            yaml.dump(important, f)

    callback(erargs, seed)


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def handle_name(name: str, player: int, name_counter: Counter):
    """Convert name option into actual player name, accounting for duplicated names"""
    name_counter[name] += 1
    new_name = "%".join([x.replace("%number%", "{number}").replace("%player%", "{player}") for x in name.split("%%")])
    new_name = string.Formatter().vformat(new_name, (), SafeDict(number=name_counter[name],
                                                                 NUMBER=(name_counter[name] if name_counter[
                                                                                                   name] > 1 else ''),
                                                                 player=player,
                                                                 PLAYER=(player if player > 1 else '')))
    new_name = new_name.strip()[:16]
    if new_name == "Archipelago":
        raise Exception(f"You cannot name yourself \"{new_name}\"")
    return new_name

# TODO: This is unused
def prefer_int(input_data: str) -> typing.Union[str, int]:
    try:
        return int(input_data)
    except:
        return input_data








if __name__ == '__main__':
    import atexit
    confirmation = atexit.register(input, "Press enter to close.")
    main()
    # in case of error-free exit should not need confirmation
    atexit.unregister(confirmation)
