"""Game options"""
import typing

from Options import Choice, Range, Option, Toggle, DefaultOnToggle

# TODO: Modularize these, handle using init.load_options
# Unused
class Objective(Choice):
    option_ganon = 0
    # option_pendants = 1
    option_triforce_pieces = 2
    option_pedestal = 3
    option_bingo = 4


# Base class for dungeon item shuffle
# Not used by itself
class DungeonItem(Choice):
    value: int
    default = 0
    option_original_dungeon = 0
    option_own_dungeons = 1
    option_own_world = 2
    option_any_world = 3
    option_different_world = 4
    alias_true = 3
    alias_false = 0
    @property
    def in_dungeon(self):
        return self.value in {0, 1}


class BigkeyShuffle(DungeonItem):
    """Choose where big keys will be placed."""
    item_name_group = "Big Keys"
    displayname = "Big Key Shuffle"


class SmallkeyShuffle(DungeonItem):
    """Choose where small keys will be placed."""
    option_universal = 5
    item_name_group = "Small Keys"
    displayname = "Small Key Shuffle"


class CompassShuffle(DungeonItem):
    """Choose where compasses will be placed."""
    item_name_group = "Compasses"
    displayname = "Compass Shuffle"


class MapShuffle(DungeonItem):
    """Choose where maps will be placed."""
    item_name_group = "Maps"
    displayname = "Map Shuffle"


# Base class for crystal requirements
# Not used by itself
class Crystals(Range):
    range_start = 0
    range_end = 7


class CrystalsTower(Crystals):
    """Choose how many crystals are needed to open Ganon's Tower."""
    displayname = "GT Crystals Required"
    default = 7


class CrystalsGanon(Crystals):
    """Choose how many crystals are needed before Ganon is vulnerable"""
    displayname = "Ganon Crystals Required"
    default = 7


class ShopItemSlots(Range):
    """Choose how many shop slots will be added to the pool"""
    displayname = "Shop Item Slots"
    default = 0

    range_start = 0
    range_end = 30

# TODO make this work and hopefully kep legacy support
class EnemyShuffle(Choice):
    """Choose the distribution of non-boss enemies. If World State is standard, Hyrule Castle
    will be left out but may have incorrect sprites"""
    displayname = "Enemy Shuffle"
    default = 0

    option_vanilla = 0
    option_shuffled = 1
    option_chaos = 2

    # Compat
    alias_false = 0
    alias_true = 1
    alias_no = 0
    alias_yes = 1
    alias_off = 0
    alias_on = 1

    # Because enemizer code expects a toggle (?)
    def __bool__(self):
        return self.value != 0

class Progressive(Choice):
    """Choose if items will progressively upgrade. Progressive items are placed
    into the world multiple times, and each collection raises the tier of that item
    until maxed."""
    displayname = "Progressive Items"
    default = 2

    option_off = 0
    option_random_for_each = 1
    option_on = 2

    alias_false = 0
    alias_true = 2
    alias_random = 1

    def want_progressives(self, random):
        return random.choice([True, False]) if self.value == self.option_grouped_random else bool(self.value)


class Swordless(Toggle):
    """No swords. Curtains in Skull Woods and Agahnim\'s
    Tower are removed, Agahnim\'s Tower barrier can be
    destroyed with hammer. Misery Mire and Turtle Rock
    can be opened without a sword. Hammer damages Ganon.
    Ether and Bombos Tablet can be activated with Hammer
    (and Book)."""
    displayname = "Swordless"


class Retro(Toggle):
    """Zelda-1 like mode. You have to purchase a quiver to shoot arrows using rupees
    and there are randomly placed take-any caves that contain one Sword and choices of Heart Container/Blue Potion."""
    displayname = "Retro"


class RestrictBossItem(Toggle):
    """Don't place dungeon-native items on the dungeon's boss."""
    displayname = "Prevent Dungeon Item on Boss"


class Hints(DefaultOnToggle):
    """Put item and entrance placement hints on telepathic tiles and some NPCs.
    Additionally King Zora and Bottle Merchant say what they're selling."""
    displayname = "Hints"

# Unused
class EnemyShuffle_Old(Toggle):
    """Randomize every enemy spawn.
    If mode is Standard, Hyrule Castle is left out (may result in visually wrong enemy sprites in that area.)"""
    displayname = "Enemy Shuffle"


class KillableThieves(Toggle):
    """Makes Thieves killable."""
    displayname = "Killable Thieves"


class BushShuffle(Toggle):
    """Randomize chance that a bush contains an enemy as well as which enemy may spawn."""
    displayname = "Bush Shuffle"


class TileShuffle(Toggle):
    """Randomize flying tiles floor patterns."""
    displayname = "Tile Shuffle"


class PotLocationShuffle(Toggle):
    """Shuffle contents of pots within "supertiles" (item will still be nearby original placement)."""
    displayname = "Pot Shuffle"


# Base class for dungeon item shuffle
# Not used by itself
class Palette(Choice):
    option_default = 0
    option_good = 1
    option_blackout = 2
    option_puke = 3
    option_classic = 4
    option_grayscale = 5
    option_negative = 6
    option_dizzy = 7
    option_sick = 8


class OWPalette(Palette):
    """The palette used when outdoors"""
    displayname = "Overworld Palette"


class UWPalette(Palette):
    """The palette used when indoors"""
    displayname = "Underworld Palette"


class HUDPalette(Palette):
    """The pallete used for the user interface"""
    displayname = "HUD Palette"


class SwordPalette(Palette):
    """The palette used for Link's sword"""
    displayname = "Sword Palette"


class ShieldPalette(Palette):
    """The palette used for Link's shield"""
    displayname = "Shield Palette"


class LinkPalette(Palette):
    """The palette used for Link's sprite"""
    displayname = "Link Palette"


class HeartBeep(Choice):
    """Choose how frequently the low health beep will play."""
    displayname = "Heart Beep Rate"
    default = 2

    option_normal = 0
    option_double = 1
    option_half = 2
    option_quarter = 3
    option_off = 4
    alias_false = 4


class HeartColor(Choice):
    """Choose the color of your hearts. Note that this sets the
    base color, which can change if HUD Palette is used."""
    displayname = "Heart Color"
    option_red = 0
    option_blue = 1
    option_green = 2
    option_yellow = 3


class QuickSwap(DefaultOnToggle):
    """Allow switching between items using L and R. Pressing both
    simultaneously will cycle between items that share a slot."""
    displayname = "L/R Quickswapping"


class MenuSpeed(Choice):
    """Choose the speed at which the menu animation plays."""
    displayname = "Menu Speed"
    option_normal = 0
    option_instant = 1,
    option_double = 2
    option_triple = 3
    option_quadruple = 4
    option_half = 5


class Music(DefaultOnToggle):
    """Play the game's background music."""
    displayname = "Play Music"


class ReduceFlashing(DefaultOnToggle):
    """Reduce the intensity and frequency of flashing effects."""
    displayname = "Reduce Screen Flashes"


class TriforceHud(Choice):
    """Choose how to display the progress of a Triforce Hunt."""
    displayname = "Triforce Hunt HUD"
    default = 0

    option_normal = 0
    option_hide_goal = 1
    option_hide_required = 2
    option_hide_both = 3

# Newly migrated as of 20 Oct 2021

class Timer(Choice):
    """Add a timer to the game UI, and cause it to have various effects."""
    displayname = "Timer"
    default = 0

    option_none = 0
    option_timed = 1
    option_timed_ohko = 2
    option_always_ohko = 3
    option_timed_countdown = 4
    option_display = 5

    alias_off = 0
    alias_disabled = 0
    alias_on = 1
    alias_enabled = 1


class DungeonCounters(DefaultOnToggle):
    """Determines when to show an on-screen counter for dungeon items."""
    displayname = "Dungeon Counters"

    option_off = 0
    option_on = 1
    alias_false = 0
    alias_true = 1


class Logic(Choice):
    """Determines what glitches will be considered in logic."""
    displayname = "Logic"
    default = 0

    option_no_glitches = 0
    option_minor_glitches = 1
    option_overworld_glitches = 2
    option_hybrid_major_glitches = 3
    option_no_logic = 4

    alias_ng = 0
    alias_owg = 2
    alias_hmg = 3


class Goal(Choice):
    """The objective of the game."""
    displayname = "Goal"
    default = 0

    option_kill_ganon = 0
    option_kill_ganon_and_agahnim_2 = 1
    option_fast_ganon = 2
    option_pedestal = 3
    option_ganon_pedestal = 4
    option_triforce_hunt = 5
    option_local_triforce_hunt = 6
    option_ganon_triforce_hunt = 7
    option_ganon_local_triforce_hunt = 8
    option_ice_rod_hunt = 9

    # compat
    alias_ganon = 0
    alias_local_ganon_triforce_hunt = 8

    @property
    def requires_ganon(self):
        return self.value in {0, 1, 2, 4, 7, 8}

    @property
    def requires_triforce(self):
        return self.value in {5, 6, 7, 8}

    @property
    def requires_pedestal(self):
        return self.value in {3, 4}


class WorldState(Choice):
    """Choose the initial state of the world. \n
    Open skips the castle escape
    sequence where you free Zelda. \n
    Inverted begins in the Dark World and inverts
    the Magic Mirror, as well as some terrain changes to ensure accessibility."""
    displayname = "World State"
    default = 0

    option_standard = 1
    option_open = 0
    option_inverted = 2


class OpenPyramid(Choice):
    """Open the Dark World pyramid before defeating Agahnim atop Ganon's Tower."""
    displayname = "Open Pyramid"
    default = 0

    option_goal = 0
    option_auto = 1
    option_yes = 2
    option_no = 3

class CountdownStartingTime(Range):
    """The initial value in minutes of the countdown timer if enabled"""
    displayname = "Countdown Starting Time"
    default = 60

    range_start = 0
    range_end = 60


class CountdownRedClockTime(Range):
    """How many minutes a red (mixed) clock adds to the timer.
    Negative values subtract time instead."""
    displayname = "Red Clock Time"
    default = -2

    range_start = -2
    range_end = 1


class CountdownBlueClockTime(Range):
    """How many minutes a blue (minor gain) clock adds to the timer."""
    displayname = "Blue Clock Time"
    default = 2

    range_start = 1
    range_end = 2


class CountdownGreenClockTime(Range):
    """How many minutes a green (major gain) clock adds to the timer."""
    displayname = "Green Clock Time"
    default = 4

    range_start = 4
    range_end = 15


# TODO: Possible change this to actually allow web name selection
# Unused
class Sprite(Option):
    """Which sprite to use"""
    displayname = "Sprite"
    default = "Link"


class Beemizer(Range):
    """Remove rupees, bombs, and arrows from the global item pool and replace them with [X%/Y%] single bees and bee traps.\n
    0: No bee traps\n
    1: Bees: [40%/60%] | Consumables: [25%]\n
    2: Bees: [30%/70%] | Consumables: [50%]\n
    3: Bees: [20%/80%] | Consumables: [75%]\n
    4: Bees: [10%/90%] | Consumables: [100%]"""
    displayname = "Beemizer"

    range_start = 0
    range_end = 4


class BossShuffle(Choice):
    """Choose the distribution of bosses."""
    displayname = "Boss Shuffle"
    default = 0

    option_none = 0
    option_simple = 1
    option_full = 2
    option_chaos = 3
    option_singularity = 4


class TriforcePiecesAvailable(Range):
    """Choose how many Triforce pieces will be placed in the pool"""
    displayname = "Triforce Pieces Available"
    default = 30

    range_start = 1
    range_end = 90


class ShopShufflePrice(Toggle):
    """Randomize shop prices"""
    displayname = "Shop Price Shuffle"


# TODO: Add an extra option to support legacy fgpuw shop shuffle
# As of now idk how this works, might come back to it
# Unused
class ShopShuffleLegacy(Choice):
    """Legacy support for gfpuw shuffling"""
    displayname = "Legacy Shop Shuffle"
    default = 0

    option_none = 0
    option_g = 1
    option_f = 2
    option_p = 3
    option_u = 4
    option_w = 5
    option_gp = 6
    option_fp = 7
    option_ufp = 8
    option_wfp = 9
    option_ufpw = 10


class ShopShufflePools(Choice):
    """Choose how to determine shop pools"""
    displayname = "Shop Pool Shuffle"

    option_none = 0
    option_shuffle_vanilla = 1
    option_random_consumables = 2
    option_random_all = 3


class ShopShuffleIncludePotionShop(Toggle):
    """Include the potion shop in shop shuffle pools"""
    displayname = "Shuffle Potion Shop"


# TODO: May not actually be possible
class ShopShuffleIncludeLakeFairy(Toggle):
    """Includes the Great Fairy of Lake Hylia in shop shuffle pools"""
    displayname = "Shuffle Lake Fairy"


class ShuffleCapacityUpgrades(Toggle):
    """Add bomb and arrow capacity upgrades to the pool"""
    displayname = "Capacity Upgrade Shuffle"


class MiseryMireMedallion(Choice):
    """Choose what medallion unlocks Misery Mire"""
    displayname = "Misery Mire Medallion"
    default = 0

    option_random_selection = 0
    option_quake = 1
    option_bombos = 2
    option_ether = 3


class TurtleRockMedallion(Choice):
    """Choose what medallion unlocks Turtle Rock"""
    displayname = "Turtle Rock Medallion"
    default = 0

    option_random_selection = 0
    option_quake = 1
    option_bombos = 2
    option_ether = 3


# TODO: Move these into their own range/choice options
class ItemPool(Choice):
    """Determines the availability of upgrades, progressive items, and convenience items.\n
    0: Twice as many upgrades.\n
    1: Standard.\n
    2: 14 hearts, remove final sword, shield, and armor, silvers only if swordless.\n
    3: 8 hearts,  remove final two swords, shields, and armors, silvers only if swordless."""
    displayname = "Item Pool"
    default = 1

    option_easy = 0
    option_normal = 1
    option_hard = 2
    option_expert = 3


# TODO: Move these into their own range/choice options
class ItemFunctionality(Choice):
    """Alters the usefulness of various items in the game.\n
    0: Medallions always usable and hammer can damage Ganon and collect tablets.\n
    1: Standard.\n
    2: Potions restore less, the Magic Cape uses 2x magic, the Cane of Byrna loses
    invincibility, bommerang does not stun, and silvers are only allowed for Ganon.\n
    3: Potions barely work, the Magic Cape uses 2x magic, the Cane of Byrna loses
    invincibility, bommerang and hookshot does not stun, and silvers are only allowed for Ganon.."""
    displayname = "Item Functionality"
    default = 1

    option_easy = 0
    option_normal = 1
    option_hard = 2
    option_expert = 3


class EnemyDamage(Choice):
    """Choose how much damage enemies deal.\n
    Shuffled: 0-4 hearts, reduced by armor.\n
    Random: 0-8 hearts, armor re-shuffles."""
    displayname = "Enemy Damage"
    default = 0

    option_vanilla = 0
    option_shuffled = 1
    option_random_damage = 2

    alias_default = 0


# TODO: Numbers for the options
class EnemyHealth(Choice):
    """Choose how much health enemies have.\n
    Reduced: Generally reduced health.\n
    Increased: Generally increased health.\n
    Armor-Plated: Greatly increased health.\n"""
    displayname = "Enemy Health"
    default = 0

    option_vanilla = 0
    option_reduced = 1
    option_increased = 2
    option_armor_plated = 3

    alias_default = 0
# 22 Oct 21


class RandomStartItemAmount(Range):
    """Start with this many random items"""
    displayname = "Random Starting Item Amount"
    default = 0

    range_start = 0
    range_end = 50 # Arbitrarily chosen

# 30 Oct 2021


class Sprite(Choice):
    """Replace Link's sprite with this one"""
    displayname = "Sprite"
    default = "link"

    option_link = "link"
    option_freya = "freya"
    option_mipha = "mipha"
    option_medli = "medli"

# 2 Nov 2021


class GlitchBoots(DefaultOnToggle):
    """Start with boots in glitched logic modes that use them"""
    displayname = "Glitch Boots"


class DarkRoomLogic(Choice):
    """Logic used for unlit dark rooms"""
    displayname = "Dark Room Logic"
    default = 0

    option_lamp = 0
    option_torches = 1
    option_none = 2


# TODO - group seeds
class EntranceShuffle(Choice):
    """How entrances will be shuffled"""
    displayname = "Entrance Shuffle"

    option_none = 0
    option_dungeons_simple = 1
    option_dungeons_full = 2
    option_dungeons_crossed = 3
    option_simple = 4
    option_restricted = 5
    option_full = 6
    option_crossed = 7
    option_insanity = 8


class ShopHeartCurrency(Toggle):
    """Allow hearts to be used as payment in shops"""
    displayname = "Shop Heart Payment"


class ShopArrowCurrency(Toggle):
    """Allow arrows to be used as payment in shops"""
    displayname = "Shop Arrow Payment"


class ShopBombCurrency(Toggle):
    """Allow bombs to be used as payment in shops"""
    displayname = "Shop Bomb Payment"


class ShopUniversalKeyCurrency(Toggle):
    """Allow universal keys to be used as payment in shops"""
    displayname = "Shop Universal Key Payment"


class ShopTriforcePieceCurrency(Toggle):
    """Allow triforce pieces to be used as payment in shops"""
    displayname = "Shop Triforce Piece Payment"


class MirrorDirection(Choice):
    """Choose which direction the Magic Mirror will transport you"""
    displayname = "Mirror Direction"
    default = 1

    option_to_dark_world = 0
    option_to_light_world = 1
    option_bidirectional = 2

    alias_standard = 1
    alias_vanilla = 1
    alias_inverted = 0


class DoorShuffle(Choice):
    """Shuffles the interior layout of dungeons"""
    displayname = "Door Shuffle"
    default = 0

    option_disabled = 0
    option_basic = 1
    option_crossed = 2

    alias_none = 0


class DoorShuffleIntensity(Choice):
    """Specifies which door types will be shuffled"""
    displayname = "Door Shuffle Intensity"
    default = 0

    option_doors_and_spiral_stairs = 0
    option_doors_edges_and_stairs = 1
    option_doors_edges_stairs_and_lobby = 2

    alias_level_1 = 0
    alias_level_2 = 1
    alias_level_3 = 2


class KeyDropShuffle(Toggle):
    """Includes keys dropped from enemies and pots in the item pool"""
    displayname = "Key Drop Shuffle"


options: typing.Dict[str, type(Option)] = {
    # Always relevant
    "goal": Goal,
    "logic": Logic,
    "dark_room_logic": DarkRoomLogic,
    "progressive": Progressive,
    "swordless": Swordless,
    "retro": Retro,
    "hints": Hints,
    "restrict_dungeon_item_on_boss": RestrictBossItem,
    "pot_location_shuffle": PotLocationShuffle,
    "key_drop_shuffle": KeyDropShuffle,
    "enemy_shuffle": EnemyShuffle_Old,
    "killable_thieves": KillableThieves,
    "bush_shuffle": BushShuffle,
    "tile_shuffle": TileShuffle,
    "world_state": WorldState,

    # Dungeon settings
    "misery_mire_medallion": MiseryMireMedallion,
    "turtle_rock_medallion": TurtleRockMedallion,
    "crystals_needed_for_gt": CrystalsTower,

    "bigkey_shuffle": BigkeyShuffle,
    "smallkey_shuffle": SmallkeyShuffle,
    "compass_shuffle": CompassShuffle,
    "map_shuffle": MapShuffle,
    "dungeon_counters": DungeonCounters,

    # Ganon Goal
    "crystals_needed_for_ganon": CrystalsGanon,
    "open_pyramid": OpenPyramid,

    # Triforce Hunt Goal
    "triforcehud": TriforceHud,
    "triforce_pieces_available": TriforcePiecesAvailable,

    # Palettes
    "ow_palettes": OWPalette,
    "uw_palettes": UWPalette,
    "hud_palettes": HUDPalette,
    "sword_palettes": SwordPalette,
    "shield_palettes": ShieldPalette,
    "link_palettes": LinkPalette,

    # Misc. Rom Settings
    "heartbeep": HeartBeep,
    "heartcolor": HeartColor,
    "quickswap": QuickSwap,
    "menuspeed": MenuSpeed,
    "music": Music,
    "reduceflashing": ReduceFlashing,
    "sprite": Sprite,

    # Shops
    "shop_item_slots": ShopItemSlots,
    "shuffle_shop_pools": ShopShufflePools,
    "shuffle_potion_shop": ShopShuffleIncludePotionShop,
    "shuffle_lake_fairy": ShopShuffleIncludeLakeFairy,
    "shuffle_capacity_upgrades": ShuffleCapacityUpgrades,
    # "shop_shuffle": ShopShuffleLegacy,
    "shuffle_shop_price": ShopShufflePrice,
    "shop_heart_currency": ShopHeartCurrency,
    "shop_bomb_currency": ShopBombCurrency,
    "shop_arrow_currency": ShopArrowCurrency,
    "shop_universal_key_currency": ShopUniversalKeyCurrency,
    "shop_triforce_piece_currency": ShopTriforcePieceCurrency,

    # Enemies
    "enemy_health": EnemyHealth,
    "enemy_damage": EnemyDamage,
    "boss_shuffle": BossShuffle,

    # Timed Mode
    "timer": Timer,
    "countdown_start_time": CountdownStartingTime,
    "red_clock_time": CountdownRedClockTime,
    "blue_clock_time": CountdownBlueClockTime,
    "green_clock_time": CountdownGreenClockTime,

    # Topography
    "entrance_shuffle": EntranceShuffle,
    "door_shuffle": DoorShuffle,
    "door_shuffle_intensity": DoorShuffleIntensity,

    # Misc
    "glitch_boots": GlitchBoots,
    "beemizer": Beemizer,
    "item_pool": ItemPool,
    "item_functionality": ItemFunctionality,
    "random_starting_item_amount": RandomStartItemAmount,
    "mirror_direction": MirrorDirection

}