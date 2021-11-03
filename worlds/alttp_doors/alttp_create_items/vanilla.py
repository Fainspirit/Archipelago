def create_vanilla_pool(autoworld):
    """Get the basic vanilla pool of 216 items. This includes inventory, hearts, consumables, and dungeon items"""
    vanilla_items = vanilla_inventory | vanilla_consumables | vanilla_dungeon_items | {'Nothing': 11} # Fix this - events and other things ?
    c = 0
    for k in vanilla_items:
        c += vanilla_items[k]
    autoworld.item_pool = vanilla_items


vanilla_inventory = {
    # Row 1
    'Bow': 1,
    'Silver Bow': 1,
    'Blue Boomerang': 1,
    'Red Boomerang': 1,
    'Hookshot': 1,
    # <Bomb slot>
    'Magic Powder': 1,
    'Mushroom': 1,

    # Row 2
    'Fire Rod': 1,
    'Ice Rod': 1,
    'Bombos': 1,
    'Quake': 1,
    'Ether': 1,

    # Row 3
    'Lamp': 1,
    'Hammer': 1,
    'Flute': 1,
    'Shovel': 1,
    'Bug Catching Net': 1,
    'Book of Mudora': 1,

    # Row 4
    'Bottle': 4,
    'Cane of Somaria': 1,
    'Cane of Byrna': 1,
    'Cape': 1,
    'Magic Mirror': 1,

    # Row 5
    'Pegasus Boots': 1,
    'Power Glove': 1,
    'Titans Mitts': 1,
    'Flippers': 1,
    'Moon Pearl': 1,

    # Equipment
    'Fighter Sword': 1,
    'Master Sword': 1,
    'Tempered Sword': 1,
    'Golden Sword': 1,
    'Blue Shield': 1,
    'Red Shield': 1,
    'Mirror Shield': 1,
    'Blue Mail': 1,
    'Red Mail': 1,
    'Sanctuary Heart Container': 1,
    'Boss Heart Container': 10,
    'Piece of Heart': 24,

    'Magic Upgrade (1/2)': 1
}
"""Base Inventory (76 count)"""

vanilla_consumables = {
    # Rupees (44 count)
    'Rupee (1)': 1, # TODO: change to "Rupees (1)" for consistency
    'Rupees (5)': 4,
    'Rupees (20)': 28,
    'Rupees (50)': 6,
    'Rupees (100)': 1,
    'Rupees (300)': 4,

    # Arrows (13 count)
    'Single Arrow': 1,
    'Arrows (10)': 12,

    # Bombs (17 count)
    'Bombs (3)': 16,
    'Bombs (10)': 1,
}
"""Consumables (74 count)"""

vanilla_dungeon_items = {
    # HC/ES
    'Small Key (Hyrule Castle)': 1,
    'Map (Hyrule Castle)': 1,

    # EP
    'Big Key (Eastern Palace)': 1,
    'Map (Eastern Palace)': 1,
    'Compass (Eastern Palace)': 1,

    # DP
    'Small Key (Desert Palace)': 1,
    'Big Key (Desert Palace)': 1,
    'Map (Desert Palace)': 1,
    'Compass (Desert Palace)': 1,

    # ToH
    'Small Key (Tower of Hera)': 1,
    'Big Key (Tower of Hera)': 1,
    'Map (Tower of Hera)': 1,
    'Compass (Tower of Hera)': 1,

    # AT
    'Small Key (Agahnims Tower)': 2,

    # PoD
    'Small Key (Palace of Darkness)': 6,
    'Big Key (Palace of Darkness)': 1,
    'Map (Palace of Darkness)': 1,
    'Compass (Palace of Darkness)': 1,

    # SP
    'Small Key (Swamp Palace)': 1,
    'Big Key (Swamp Palace)': 1,
    'Map (Swamp Palace)': 1,
    'Compass (Swamp Palace)': 1,

    # SW
    'Small Key (Skull Woods)': 3,
    'Big Key (Skull Woods)': 1,
    'Map (Skull Woods)': 1,
    'Compass (Skull Woods)': 1,

    # TT
    'Small Key (Thieves Town)': 1,
    'Big Key (Thieves Town)': 1,
    'Map (Thieves Town)': 1,
    'Compass (Thieves Town)': 1,

    # IP
    'Small Key (Ice Palace)': 2,
    'Big Key (Ice Palace)': 1,
    'Map (Ice Palace)': 1,
    'Compass (Ice Palace)': 1,

    # MM
    'Small Key (Misery Mire)': 3,
    'Big Key (Misery Mire)': 1,
    'Map (Misery Mire)': 1,
    'Compass (Misery Mire)': 1,

    # TR
    'Small Key (Turtle Rock)': 4,
    'Big Key (Turtle Rock)': 1,
    'Map (Turtle Rock)': 1,
    'Compass (Turtle Rock)': 1,

    # GT
    'Small Key (Ganons Tower)': 4,
    'Big Key (Ganons Tower)': 1,
    'Map (Ganons Tower)': 1,
    'Compass (Ganons Tower)': 1,
}
"""Dungeon Items (63 count)"""
