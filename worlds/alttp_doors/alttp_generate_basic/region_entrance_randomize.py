from ..region_randomizer import RegionRandomizer
from ..alttp_create_regions import entrance_flags

def randomize_region_entrances(autoworld):

    rergp = RegionRandomizer.RegionEntranceRandomizerGenericParameters()

    rer = RegionRandomizer.RegionEntranceRandomizer(
        [], #autoworld.regions,
        {},
        entrance_flags.EntranceType,
        rergp,
        "aLttP"
    )

    rer.randomize_entrances()

