import logging


def pre_fill(self):
    from Fill import fill_restrictive, FillError
    attempts = 5
    world = self.world
    player = self.player
    lttp_logger = logging.getLogger("A Link to the Past + Doors")

    all_state = world.get_all_state(use_cache=True)
    crystals = [self.create_item(name) for name in
                ['Red Pendant', 'Blue Pendant', 'Green Pendant', 'Crystal 1', 'Crystal 2', 'Crystal 3', 'Crystal 4',
                 'Crystal 7', 'Crystal 5', 'Crystal 6']]
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
            # TODO: replace this
            lttp_logger.exception("Failed to place dungeon prizes (%s). Will retry %s more times", e,
                                  attempts - attempt)
            for location in empty_crystal_locations:
                location.item = None
            continue
        break
    else:
        raise FillError('Unable to place dungeon prizes')