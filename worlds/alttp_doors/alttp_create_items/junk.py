import random

junk_pool = [
    "Rupee (1)",
    "Rupees (5)",
    "Rupees (20)",
    "Rupees (50)",
    "Rupees (100)",
    "Rupees (300)",

    "Single Arrow",
    "Arrows (10)",

    "Bombs (3)",
    "Bombs (10)"
]

weights = [
    1, 4, 28, 7, 1, 5,
    1, 12,
    16, 1
]

def handle_junk(autoworld):
    locations = [] #autoworld.locations
    location_count = 216 # TODO - dynamic location count
    num_needed = location_count - autoworld.metadata["item_pool_size"] # TODO - do this based on current size
    add_junk(autoworld, num_needed)



def add_junk(autoworld, amount):
    autoworld.metadata["item_pool_size"] += amount

    keys = random.choices(junk_pool, weights, k=amount)
    for k in keys:
        if k not in autoworld.item_pool:
            autoworld.item_pool[k] = 1
        else:
            autoworld.item_pool[k] += 1