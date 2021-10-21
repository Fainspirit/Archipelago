import os
import Patch

from .legacy.Rom import LocalRom, patch_rom, patch_race_rom, patch_enemizer, apply_rom_settings, get_hash_string, \
    get_base_rom_path


def write_rom(autoworld, output_directory: str):
    """Apply selected settings to the rom and save it in /output"""
    world = autoworld.world
    player = autoworld.player

    try:
        use_enemizer = (world.boss_shuffle[player] != 'none' or world.enemy_shuffle[player]
                        or world.enemy_health[player] != 'default' or world.enemy_damage[player] != 'default'
                        or world.pot_shuffle[player] or world.bush_shuffle[player]
                        or world.killable_thieves[player])

        rom = LocalRom(get_base_rom_path())

        patch_rom(world, rom, player, use_enemizer)

        if use_enemizer:
            patch_enemizer(world, player, rom, world.enemizer, output_directory)

        if world.is_race:
            patch_race_rom(rom, world, player)

        world.spoiler.hashes[player] = get_hash_string(rom.hash)

        palettes_options = {
            'dungeon': world.uw_palettes[player],
            'overworld': world.ow_palettes[player],
            'hud': world.hud_palettes[player],
            'sword': world.sword_palettes[player],
            'shield': world.shield_palettes[player],
            'link': world.link_palettes[player]
        }
        palettes_options = {key: option.current_key for key, option in palettes_options.items()}

        # User customization
        apply_rom_settings(rom, world.heartbeep[player].current_key,
                           world.heartcolor[player].current_key,
                           world.quickswap[player],
                           world.menuspeed[player].current_key,
                           world.music[player],
                           world.sprite[player],
                           palettes_options, world, player, True,
                           reduceflashing=world.reduceflashing[player] or world.is_race,
                           triforcehud=world.triforcehud[player].current_key)

        # Write modified ROM to disk
        outfilepname = f'_P{player}'
        outfilepname += f"_{world.player_names[player].replace(' ', '_')}" \
            if world.player_names[player] != 'Player%d' % player else ''

        rompath = os.path.join(output_directory, f'AP_{world.seed_name}{outfilepname}.sfc')
        rom.write_to_file(rompath)
        Patch.create_patch_file(rompath, player=player, player_name=world.player_names[player])
        os.unlink(rompath)
        autoworld.rom_name = rom.name
    except:
        raise
    finally:
        autoworld.rom_name_available_event.set()  # make sure threading continues and errors are collected
