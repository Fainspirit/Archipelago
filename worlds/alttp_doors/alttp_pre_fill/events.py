def handle_events(autoworld):
    event_pairs = [
        ('Agahnim 1', 'Beat Agahnim 1'),
        ('Agahnim 2', 'Beat Agahnim 2'),
        ('Dark Blacksmith Ruins', 'Pick Up Purple Chest'),
        ('Frog', 'Get Frog'),
        ('Missing Smith', 'Return Smith'),
        ('Floodgate', 'Open Floodgate'),
        ('Agahnim 1', 'Beat Agahnim 1'),
        ('Flute Activation Spot', 'Activated Flute')
    ]

    for location_name, event_name in event_pairs:
        location = autoworld.world.get_location(location_name, autoworld.player)
        event = autoworld.create_item(event_name)
        autoworld.world.push_item(location, event, False)
        location.event = location.locked = True