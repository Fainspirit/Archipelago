from BaseClasses import Region, RegionType, Location
import time

class RegionExitRandomizerGenericParameters:
    """A class to hold parameters for RegionRandomizer"""
    def __init__(self, max_time: float = 99999, shuffle_count = 500, sanity_check = True):

        self.max_time = max_time
        self.shuffle_count = shuffle_count
        self.sanity_check = sanity_check

class RegionContainer:
    def __init__(self, region: Region, seen: bool = False, index: int = -1):
        self.region = region
        self.seen = seen
        self.index = index

class RegionExitRandomizer:
    def __init__(self, regions: list[Region], params: RegionExitRandomizerGenericParameters, name: str = ""):
        """A class to randomize game regions"""

        # Region dict to get any region and it's data by name
        self.region_containers = {r.name: RegionContainer(r) for r in regions}

        # General parameters
        self.params = params

        # Optional name
        self.name = name

        # Used to store exit swap options
        self.candidate_lists = {}

        # Used for the DFS enumeration of game state
        self.exit_stack = []

        # Used to maintain a possible completable game
        self.linear_path = []


    # TODO - Ensure that the game state holds for at least one traversal
    def sanity_check(self):
        return self.region_containers.count() > 0


    def build_linear_path(self):
        # Start with the menu
        start_region = self.region_containers['Menu'].region



    def shuffle_exit(self):
        pass


    def explore_region(self, region_name: str):
        """Explore a region and update the state. This assumes
        that it is actually possible to visit this region"""

        # Mark as visited
        self.region_containers[region_name].seen = True

        # Add this region as the next "
        # Add the region's exits to the stack so that they get explored
        self.exit_stack.append(self.regions['Menu'].exits)

    def randomize_exits(self):
        # Sanity check to verify the game is beatable
        # Takes time but can be useful
        if self.params.sanity_check:
            if not self.sanity_check(self):
                raise Exception(f"Sanity check failed")

        cycles = 0
        start_time = time.time()

        # Randomize, respecting the time and count constraints
        while cycles < self.params.shuffle_count and time.time() - self.params.max_time < start_time:
            self.shuffle_exit(self)

    pass
