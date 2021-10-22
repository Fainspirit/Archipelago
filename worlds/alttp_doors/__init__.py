from worlds.AutoWorld import World
from typing import Optional, Tuple, List, Dict, Set

from BaseClasses import Item, CollectionState, Location, MultiWorld
from Options import Option
from worlds.alttp_doors import memory_data

from worlds.alttp_doors.init.load_options import load_options
from worlds.alttp_doors.memory_data.location_data import location_table
from worlds.alttp_doors.memory_data.region_data import lookup_name_to_id
from worlds.alttp_doors.legacy.item_data import item_name_groups, item_table


class ALTTPDoorsWorld(World):
    """
    The Legend of Zelda: A Link to the Past is an action/adventure game. Take on the role of
    Link, a boy who is destined to save the land of Hyrule. Delve through three palaces and nine
    dungeons on your quest to rescue the descendants of the seven wise men and defeat the evil
    Ganon!

    Now with door randomization!
    """

    options: Dict[str, type(Option)] = load_options() # link your Options mapping
    game: "A Link to the Past + Doors"  # name the game
    topology_present: bool = True  # indicate if world type has any meaningful layout/pathing
    all_names: Set[str] = frozenset()  # gets automatically populated with all item, item group and location names

    # map names to their IDs
    item_name_to_id: Dict[str, int] = {name: data.item_code for name, data in item_table.items() if type(data.item_code) == int}
    location_name_to_id: Dict[str, int] = lookup_name_to_id

    # maps item group names to sets of items. Example: "Weapons" -> {"Sword", "Bow"}
    item_name_groups: Dict[str, Set[str]] = item_name_groups

    # increment this every time something in your world's names/id mappings changes.
    # While this is set to 0 in *any* AutoWorld, the entire DataPackage is considered in testing mode and will be
    # retrieved by clients on every connection.
    data_version: int = 1

    hint_blacklist: Set[str] = frozenset({"Triforce"})  # any names that should not be hintable

    # if a world is set to remote_items, then it just needs to send location checks to the server and the server
    # sends back the items
    # if a world is set to remote_items = False, then the server never sends an item where receiver == finder,
    # the client finds its own items in its own world.
    remote_items: bool = False

    # If remote_start_inventory is true, the start_inventory/world.precollected_items is sent on connection,
    # otherwise the world implementation is in charge of writing the items to their output data.
    remote_start_inventory: bool = False

    # For games where after a victory it is impossible to go back in and get additional/remaining Locations checked.
    # this forces forfeit:  auto for those games.
    forced_auto_forfeit: bool = True

    # Hide World Type from various views. Does not remove functionality.
    hidden: bool = False

    # autoset on creation:
    world: MultiWorld
    player: int

    # automatically generated
    item_id_to_name: Dict[int, str]
    location_id_to_name: Dict[int, str]

    item_names: Set[str]  # set of all potential item names
    location_names: Set[str]  # set of all potential location names

    # If there is visibility in what is being sent, this is where it will be known.
    sending_visible: bool = False

    def __init__(self, world: MultiWorld, player: int):
        self.world = world
        self.player = player

    # overridable methods that get called by Main.py, sorted by execution order
    # can also be implemented as a classmethod and called "stage_<original_name",
    # in that case the MultiWorld object is passed as an argument and it gets called once for the entire multiworld.
    # An example of this can be found in alttp as stage_pre_fill
    def generate_early(self):
        pass

    def create_regions(self):
        pass

    def create_items(self):
        pass

    def set_rules(self):
        pass

    def generate_basic(self):
        pass

    def pre_fill(self):
        """Optional method that is supposed to be used for special fill stages. This is run *after* plando."""
        pass

    def fill_hook(cls, progitempool: List[Item], nonexcludeditempool: List[Item],
                  localrestitempool: Dict[int, List[Item]], nonlocalrestitempool: Dict[int, List[Item]],
                  restitempool: List[Item], fill_locations: List[Location]):
        """Special method that gets called as part of distribute_items_restrictive (main fill).
        This gets called once per present world type."""
        pass

    def post_fill(self):
        """Optional Method that is called after regular fill. Can be used to do adjustments before output generation."""

    def generate_output(self, output_directory: str):
        """This method gets called from a threadpool, do not use world.random here.
        If you need any last-second randomization, use MultiWorld.slot_seeds[slot] instead."""
        pass

    def fill_slot_data(self) -> dict:
        """Fill in the slot_data field in the Connected network package."""
        return {}

    def modify_multidata(self, multidata: dict):
        """For deeper modification of server multidata."""
        pass

    def get_required_client_version(self) -> Tuple[int, int, int]:
        return 0, 1, 6

    # end of ordered Main.py calls

    def collect_item(self, state: CollectionState, item: Item, remove: bool = False) -> Optional[str]:
        """Collect an item name into state. For speed reasons items that aren't logically useful get skipped.
        Collect None to skip item.
        :param remove: indicate if this is meant to remove from state instead of adding."""
        if item.advancement:
            return item.name

    def create_item(self, name: str) -> Item:
        """Create an item for this world type and player.
        Warning: this may be called with self.world = None, for example by MultiServer"""
        raise NotImplementedError