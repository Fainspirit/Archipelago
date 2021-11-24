def handle_crystals(autoworld):
    # TODO - fix this kek
    print("handle crystals")

    world = autoworld.world
    player = autoworld.player

    crystals = [autoworld.create_item(name) for name in
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

    world.random.shuffle(crystal_locations)

    for l in crystal_locations:
        world.push_item(l, crystals.pop(), False)

