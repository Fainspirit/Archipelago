import typing

from worlds.alttp_doors.legacy.item_pool import difficulties


def generate_early(self):
    player = self.player
    world = self.world

    # system for sharing ER layouts
    self.er_seed = str(world.random.randint(0, 2 ** 64))

    if "-" in world.shuffle[player]:
        shuffle, seed = world.shuffle[player].split("-", 1)
        world.shuffle[player] = shuffle
        if shuffle == "vanilla":
            self.er_seed = "vanilla"
        elif seed.startswith("group-") or world.is_race:
            self.er_seed = get_same_seed(world, (
                shuffle, seed, world.retro[player], world.mode[player], world.logic[player]))
        else:  # not a race or group seed, use set seed as is.
            self.er_seed = seed
    elif world.shuffle[player] == "vanilla":
        self.er_seed = "vanilla"
    for dungeon_item in ["smallkey_shuffle", "bigkey_shuffle", "compass_shuffle", "map_shuffle"]:
        option = getattr(world, dungeon_item)[player]
        if option == "own_world":
            world.local_items[player].value |= self.item_name_groups[option.item_name_group]
        elif option == "different_world":
            world.non_local_items[player].value |= self.item_name_groups[option.item_name_group]
        elif option.in_dungeon:
            self.dungeon_local_item_names |= self.item_name_groups[option.item_name_group]
            if option == "original_dungeon":
                self.dungeon_specific_item_names |= self.item_name_groups[option.item_name_group]

    world.difficulty_requirements[player] = difficulties[world.difficulty[player]]

def get_same_seed(world, seed_def: tuple) -> str:
    seeds: typing.Dict[tuple, str] = getattr(world, "__named_seeds", {})
    if seed_def in seeds:
        return seeds[seed_def]
    seeds[seed_def] = str(world.random.randint(0, 2 ** 64))
    world.__named_seeds = seeds
    return seeds[seed_def]