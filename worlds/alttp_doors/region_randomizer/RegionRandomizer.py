import random
from collections import deque
from enum import Enum, IntFlag
from typing import Dict, Type

from BaseClasses import Region, RegionType, Location, Entrance
import time


class RegionEntranceRandomizerGenericParameters:
    """A class to hold parameters for RegionRandomizer"""
    def __init__(self, max_time_seconds: float = 60, shuffle_count = 1500, sanity_check = True):

        self.max_time_seconds = max_time_seconds
        self.shuffle_count = shuffle_count
        self.sanity_check = sanity_check


class RegionContainer:
    def __init__(self,
                 region: Region,
                 seen: bool = False,
                 index: int = -1,
                 current_region_type: str = "none",
                 free_space_state: Dict[str, int] = {},
                 collected_state: Dict[str, int] = {}):
        """Holds a game region and metadata"""

        # The region - contains locations
        self.region = region

        # If we have already traversed this region
        self.seen = seen

        # The index in the linear path that this region falls in
        self.index = index

        # The current type of the region. Eg. dungeon #
        self.current_region_type = current_region_type

        # What is "free" that can be used to pay for future costs
        self.free_space_state = free_space_state
        # ex: {"Overworld": 5, "HC": 1}

        # What is already available and does not need to be used for future costs
        self.collected_state = collected_state

        # Borrowed space oh no
        self.borrowed_space = 0


    # TODO - make dict update via method so that borrowd space can update per edit instead of query based
    # Sum the non-any space that's available
    def max_borrowed_space(self):
        n = 0
        for k in self.free_space_state:
            if k is not 'any':
                n += self.free_space_state[k]

    def add_free_space(self, key, value):
        pass # Adjust borrow cap  # TODO

    def claim_free_space(self, key, value):
        pass # Check against borrow cap, update borrow if any # TODO

    def can_claim_free_space(self, key, value):
        pass # return whether available space and borrow let you do so


class EntranceContainer:
    def __init(self,
               entrance: Entrance,
               entrance_region_type: str,
               entrance_flags: IntFlag,
               cost:Dict[str, int] = None):
        """Holds a game entrance and metadata"""

        # The entrance - specifies exit and rules
        self.entrance = entrance

        # Specifies logical areas - Dungeon1, Dungeon2, overworld
        # The current traversal state will be based on this
        self.entrance_region_type = entrance_region_type

        # TODO - specify somewhere in the params what types of flags are interchangable
        # The IntFlags objects describing this entrance's flags
        self.entrance_flags = entrance_flags

        # The cost in "free space" to take this entrance
        self.cost = cost


# TODO - Need to pass a list of all that can be had in a state? ("hookshot, small key, boomerang") for collection state
# TODO - Need to pass a list of checks and their type? (check type based on region type of the traversal)
class RegionEntranceRandomizer:
    def __init__(self,
                 regions: list[Region],
                 entrance_containers: Dict[str, EntranceContainer],
                 entrance_type_class: Type[IntFlag],
                 params: RegionEntranceRandomizerGenericParameters,
                 name: str = ""):
        """A class to randomize game regions"""

        # Region dict to get any region and its data by name
        self.region_containers = {r.name: RegionContainer(r) for r in regions}

        # Entrance dict to access any entrance and its data by name
        self.entrance_containers = entrance_containers

        # The IntFlags class describing what flags the entrance can have set
        self.entrance_classes = entrance_type_class # TODO cache

        # General parameters
        self.params = params

        # Optional name
        self.name = name

        # Used to store exit swap options
        self.candidate_lists = {}

        # Used for the DFS enumeration of game state
        self.entrance_container_deque = deque()

        # Used to maintain a possible completable game
        self.linear_region_container_path = []

    # TODO - Ensure that the game state holds for at least one traversal
    def sanity_check(self):
        return self.region_containers.__len__() >= 0

    def build_linear_region_container_path(self):
        # Start with the menu region
        current_region_container = self.region_containers['Menu'].region

        # Add entrance containers corresponding to the entrances in the current region
        # Special case for start region
        self.entrance_container_deque.append(self.entrance_containers[e.name] for e in current_region_container.region.entrances)

        # TODO - identify infinite loops (single entrance that cannot be used etc) and abort
        # While we have entrances to explore...
        while self.entrance_container_deque.__len__() > 0:
            ec = self.entrance_container_stack.pop()

            # If this edge can be traversed...
            if self.can_take_entrance_in_from(ec, current_region_container):
                # Region exploration step:
                
                # Add entrance containers corresponding to the entrances in the current region
                self.entrance_container_deque.append(
                    self.entrance_containers[e.name] for e in current_region_container.region.entrances)
                
                # Add the region container to our linear gameplay path
                self.linear_region_container_path.append(current_region_container)

                # Update its index
                cur_index = self.linear_region_container_path.__len__() - 1
                current_region_container.index = cur_index
                
                # Copy previous state to here
                if (cur_index > 1):
                    current_region_container.collected_state = self.linear_region_container_path[cur_index - 1].collected_state
                    current_region_container.free_space_state = self.linear_region_container_path[cur_index - 1].free_space_state

                # Add new locations the prior availability state based on locations and edge type
                # as edge type determines where we are *now*. Needed when items are restricted to be
                # in a certain type of area, such as a specific dungeon
                check_type = ec.entrance_region_type

                # TODO - location requirements, add them to a queue too to come back to
                # For each of the location (naive assuming you can get there), add a space
                # To the free space state
                for l in current_region_container.region.locations:
                    if check_type in current_region_container:
                        current_region_container.free_space_state[check_type] += 1
                    else:
                        current_region_container.free_space_state[check_type] = 1


            else: # Can't traverse now, put it at the end and we try later once we have lots more space
                self.entrance_container_deque.appendleft(ec)

    # TODO - item name wrapper to indicate reusability
    def item_is_reusable(self, item):
        # Small key, bombs: no
        # Big key, hookshot: yes
        return True

    # TODO region type too for item wrapper
    # dungeon items will have their dungeon
    # other things may have data too
    def item_required_region_type(self, item):
        return 'any'

    # TODO - use this with flag masking to see which entrances are valid swaps
    def can_take_entrance_in_from(self, entrance_container, current_region_container):
        # If all can be paid for...
        # TODO - have temp borrow / used costs so that if you have 2 items that need 3, you need 6 to satisfy
        # TODO - better idea, build up all true costs per region type, then check borrow all at once!
        for item in entrance_container.cost:
            # ex {"HC_key": 1}

            # We don't need to pay costs to obtain things we have
            if item in current_region_container.collected_state and self.item_is_reusable(item):
                continue # We already have it, move along #item_cost = 0 #entrance_container.cost[item] - current_region_container.collected_state[item]
            else:
                item_cost = entrance_container.cost[item]

            required_region_type = self.item_required_region_type(item)

            # If we have enough space to "claim" the item in the region it wants...
            if current_region_container.free_space_state[required_region_type] >= item_cost:
                # Say that we can do it!
                continue # TODO - return how "easy" this is, or how much space we still have? Could be good to prioritize "opening up"
            else: # need to check borrow logic
                if current_region_container.can_claim_free_space(item, item_cost):
                    continue # If we can claim space for this item
                return False
                # TODO - enforce this borrow logic!
                # If so, we have to borrow against all other types, so we make note
                # That we did that. Need to make sure that the sum of space in all
                # non 'any' regions is greater than the borrow!

        # Return True
        return True

    def take_entrance_in_from(self, entrance_container, current_region_container):
        # TODO - maybe check as above, but update state
        pass
        # Assume valid? is faster but prone to error
        # Allocate that space to the item
        # current_region_container.free_space_state[required_region_type] -= item_cost

    def shuffle_exit(self, entrance_container: EntranceContainer):
        pass

    def explore_region(self, region_name: str):
        """Explore a region and update the state. This assumes
        that it is actually possible to visit this region"""

        # Mark as visited
        self.region_containers[region_name].seen = True

        # Add this region as the next "
        # Add the region's exits to the stack so that they get explored
        self.entrance_container_stack.append(self.regions['Menu'].exits)


    def randomize_entrances(self):
        # Sanity check to verify the game is beatable
        # Takes time but can be useful
        if self.params.sanity_check:
            if not self.sanity_check():
                raise Exception(f"[RegionRandomizer] {self.name}: Sanity check failed")

        cycles = 0
        start_time = time.time()

        # Don't do anything if zero entrance container count.
        if self.entrance_containers.__len__() > 0:
            # Randomize, respecting the time and count constraints
            while cycles < self.params.shuffle_count and time.time() - self.params.max_time_seconds < start_time:
                entrance_container = random.choice(self.entrance_containers)
                self.shuffle_exit(entrance_container)

    pass
