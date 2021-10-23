from __future__ import annotations
from typing import List, Optional, Set
import logging

from worlds.alttp_doors.standard.sub_classes import ALttPDoorsLocation
from worlds.alttp_doors.legacy.shop import Shop, shop_class_mapping, price_to_funny_price, ShopData, shop_table_by_location, ShopType
from worlds.alttp_doors.legacy.item_data import item_table, ItemFactory, trap_replaceable, GetBeemizerItem
from worlds.alttp_doors.options.standard import smallkey_shuffle

logger = logging.getLogger("Shops")


def FillDisabledShopSlots(world):
    shop_slots: Set[ALttPDoorsLocation] = {location for shop_locations in (shop.region.locations for shop in world.shops)
                                      for location in shop_locations
                                      if location.shop_slot is not None and location.shop_slot_disabled}
    for location in shop_slots:
        location.shop_slot_disabled = True
        shop: Shop = location.parent_region.shop
        location.item = ItemFactory(shop.inventory[location.shop_slot]['item'], location.player)
        location.item_rule = lambda item: item.name == location.item.name and item.player == location.player


def ShopSlotFill(world):
    shop_slots: Set[ALttPDoorsLocation] = {location for shop_locations in (shop.region.locations for shop in world.shops)
                                      for location in shop_locations if location.shop_slot is not None}
    removed = set()
    for location in shop_slots:
        shop: Shop = location.parent_region.shop
        if not shop.can_push_inventory(location.shop_slot) or location.shop_slot_disabled:
            location.shop_slot_disabled = True
            removed.add(location)

    if removed:
        shop_slots -= removed

    if shop_slots:
        logger.info("Filling LttP Shop Slots")
        del shop_slots

        from Fill import swap_location_item
        # TODO: allow each game to register a blacklist to be used here?
        blacklist_words = {"Rupee"}
        blacklist_words = {item_name for item_name in item_table if any(
            blacklist_word in item_name for blacklist_word in blacklist_words)}
        blacklist_words.add("Bee")

        locations_per_sphere = list(
            sorted(sphere, key=lambda location: location.name) for sphere in world.get_spheres())

        # currently special care needs to be taken so that Shop.region.locations.item is identical to Shop.inventory
        # Potentially create Locations as needed and make inventory the only source, to prevent divergence
        cumu_weights = []
        shops_per_sphere = []
        candidates_per_sphere = []

        # sort spheres into piles of valid candidates and shops
        for sphere in locations_per_sphere:
            current_shops_slots = []
            current_candidates = []
            shops_per_sphere.append(current_shops_slots)
            candidates_per_sphere.append(current_candidates)
            for location in sphere:
                if location.shop_slot is not None:
                    if not location.shop_slot_disabled:
                        current_shops_slots.append(location)
                elif not location.locked and not location.item.name in blacklist_words:
                    current_candidates.append(location)
            if cumu_weights:
                x = cumu_weights[-1]
            else:
                x = 0
            cumu_weights.append(len(current_candidates) + x)

            world.random.shuffle(current_candidates)

        del locations_per_sphere

        for i, current_shop_slots in enumerate(shops_per_sphere):
            if current_shop_slots:
                # getting all candidates and shuffling them feels cpu expensive, there may be a better method
                candidates = [(location, i) for i, candidates in enumerate(candidates_per_sphere[i:], start=i)
                              for location in candidates]
                world.random.shuffle(candidates)
                for location in current_shop_slots:
                    shop: Shop = location.parent_region.shop
                    for index, (c, swapping_sphere_id) in enumerate(candidates):  # chosen item locations
                        if c.item_rule(location.item) and location.item_rule(c.item):
                            swap_location_item(c, location, check_locked=False)
                            logger.debug(f'Swapping {c} into {location}:: {location.item}')
                            # remove candidate
                            candidates_per_sphere[swapping_sphere_id].remove(c)
                            candidates.pop(index)
                            break

                    else:
                        # This *should* never happen. But let's fail safely just in case.
                        logger.warning("Ran out of ShopShuffle Item candidate locations.")
                        location.shop_slot_disabled = True
                        continue

                    item_name = location.item.name
                    if location.item.game != "A Link to the Past":
                        price = world.random.randrange(1, 28)
                    elif any(x in item_name for x in
                             ['Compass', 'Map', 'Single Bomb', 'Single Arrow', 'Piece of Heart']):
                        price = world.random.randrange(1, 7)
                    elif any(x in item_name for x in ['Arrow', 'Bomb', 'Clock']):
                        price = world.random.randrange(2, 14)
                    elif any(x in item_name for x in ['Small Key', 'Heart']):
                        price = world.random.randrange(4, 28)
                    else:
                        price = world.random.randrange(8, 56)

                    shop.push_inventory(location.shop_slot, item_name, price * 5, 1,
                                        location.item.player if location.item.player != location.player else 0)
                    if 'P' in world.shop_shuffle[location.player]:
                        price_to_funny_price(shop.inventory[location.shop_slot], world, location.player)


def create_shops(world, player: int):
    from worlds.alttp_doors.legacy.shop import shop_table, _basic_shop_defaults, _dark_world_shop_defaults, _inverted_hylia_shop_defaults, total_dynamic_shop_slots

    option = world.shop_shuffle[player]

    player_shop_table = shop_table.copy()
    if "w" in option:
        player_shop_table["Potion Shop"] = player_shop_table["Potion Shop"]._replace(locked=False)
        dynamic_shop_slots = total_dynamic_shop_slots + 3
    else:
        dynamic_shop_slots = total_dynamic_shop_slots

    num_slots = min(dynamic_shop_slots, world.shop_item_slots[player])
    single_purchase_slots: List[bool] = [True] * num_slots + [False] * (dynamic_shop_slots - num_slots)
    world.random.shuffle(single_purchase_slots)

    if 'g' in option or 'f' in option:
        default_shop_table = [i for l in
                              [shop_generation_types[x] for x in ['arrows', 'bombs', 'potions', 'shields', 'bottle'] if
                               not world.retro[player] or x != 'arrows'] for i in l]
        new_basic_shop = world.random.sample(default_shop_table, k=3)
        new_dark_shop = world.random.sample(default_shop_table, k=3)
        for name, shop in player_shop_table.items():
            typ, shop_id, keeper, custom, locked, items, sram_offset = shop
            if not locked:
                new_items = world.random.sample(default_shop_table, k=3)
                if 'f' not in option:
                    if items == _basic_shop_defaults:
                        new_items = new_basic_shop
                    elif items == _dark_world_shop_defaults:
                        new_items = new_dark_shop
                keeper = world.random.choice([0xA0, 0xC1, 0xFF])
                player_shop_table[name] = ShopData(typ, shop_id, keeper, custom, locked, new_items, sram_offset)
    if world.mode[player] == "inverted":
        # make sure that blue potion is available in inverted, special case locked = None; lock when done.
        player_shop_table["Dark Lake Hylia Shop"] = \
            player_shop_table["Dark Lake Hylia Shop"]._replace(items=_inverted_hylia_shop_defaults, locked=None)
    chance_100 = int(world.retro[player]) * 0.25 + int(
        world.smallkey_shuffle[player] == smallkey_shuffle.option_universal) * 0.5
    for region_name, (room_id, type, shopkeeper, custom, locked, inventory, sram_offset) in player_shop_table.items():
        region = world.get_region(region_name, player)
        shop: Shop = shop_class_mapping[type](region, room_id, shopkeeper, custom, locked, sram_offset)
        # special case: allow shop slots, but do not allow overwriting of base inventory behind them
        if locked is None:
            shop.locked = True
        region.shop = shop
        world.shops.append(shop)
        for index, item in enumerate(inventory):
            shop.add_inventory(index, *item)
            if not locked and num_slots:
                slot_name = f"{region.name} {shop.slot_names[index]}"
                loc = ALttPDoorsLocation(player, slot_name, address=shop_table_by_location[slot_name],
                                    parent=region, hint_text="for sale")
                loc.shop_slot = index
                loc.locked = True
                if single_purchase_slots.pop():
                    if world.goal[player] != 'icerodhunt':
                        if world.random.random() < chance_100:
                            additional_item = 'Rupees (100)'
                        else:
                            additional_item = 'Rupees (50)'
                    else:
                        additional_item = GetBeemizerItem(world, player, 'Nothing')
                    loc.item = ItemFactory(additional_item, player)
                else:
                    loc.item = ItemFactory(GetBeemizerItem(world, player, 'Nothing'), player)
                    loc.shop_slot_disabled = True
                loc.item.world = world
                shop.region.locations.append(loc)
                world.dynamic_locations.append(loc)
                world.clear_location_cache()









shop_generation_types = {
    'arrows': [('Single Arrow', 5), ('Arrows (10)', 50)],
    'bombs': [('Single Bomb', 10), ('Bombs (3)', 30), ('Bombs (10)', 50)],
    'shields': [('Red Shield', 500), ('Blue Shield', 50)],
    'potions': [('Red Potion', 150), ('Green Potion', 90), ('Blue Potion', 190)],
    'discount_potions': [('Red Potion', 120), ('Green Potion', 60), ('Blue Potion', 160)],
    'bottle': [('Small Heart', 10), ('Apple', 50), ('Bee', 10), ('Good Bee', 100), ('Faerie', 100), ('Magic Jar', 100)],
    'time': [('Red Clock', 100), ('Blue Clock', 200), ('Green Clock', 300)],
}


def set_up_shops(world, player: int):
    # TODO: move hard+ mode changes for shields here, utilizing the new shops

    if world.retro[player]:
        rss = world.get_region('Red Shield Shop', player).shop
        replacement_items = [['Red Potion', 150], ['Green Potion', 75], ['Blue Potion', 200], ['Bombs (10)', 50],
                             ['Blue Shield', 50], ['Small Heart',
                                                   10]]  # Can't just replace the single arrow with 10 arrows as retro doesn't need them.
        if world.smallkey_shuffle[player] == smallkey_shuffle.option_universal:
            replacement_items.append(['Small Key (Universal)', 100])
        replacement_item = world.random.choice(replacement_items)
        rss.add_inventory(2, 'Single Arrow', 80, 1, replacement_item[0], replacement_item[1])
        rss.locked = True

    if world.smallkey_shuffle[player] == smallkey_shuffle.option_universal or world.retro[player]:
        for shop in world.random.sample([s for s in world.shops if
                                         s.custom and not s.locked and s.type == ShopType.Shop and s.region.player == player],
                                        5):
            shop.locked = True
            slots = [0, 1, 2]
            world.random.shuffle(slots)
            slots = iter(slots)
            if world.smallkey_shuffle[player] == smallkey_shuffle.option_universal:
                shop.add_inventory(next(slots), 'Small Key (Universal)', 100)
            if world.retro[player]:
                shop.push_inventory(next(slots), 'Single Arrow', 80)


def shuffle_shops(world, items, player: int):
    option = world.shop_shuffle[player]
    if 'u' in option:
        progressive = world.progressive[player]
        progressive = world.random.choice([True, False]) if progressive == 'grouped_random' else progressive == 'on'
        progressive &= world.goal == 'icerodhunt'
        new_items = ["Bomb Upgrade (+5)"] * 6
        new_items.append("Bomb Upgrade (+5)" if progressive else "Bomb Upgrade (+10)")

        if not world.retro[player]:
            new_items += ["Arrow Upgrade (+5)"] * 6
            new_items.append("Arrow Upgrade (+5)" if progressive else "Arrow Upgrade (+10)")

        world.random.shuffle(new_items)  # Decide what gets tossed randomly if it can't insert everything.

        capacityshop: Optional[Shop] = None
        for shop in world.shops:
            if shop.type == ShopType.UpgradeShop and shop.region.player == player and \
                    shop.region.name == "Capacity Upgrade":
                shop.clear_inventory()
                capacityshop = shop

        if world.goal[player] != 'icerodhunt':
            for i, item in enumerate(items):
                if item.name in trap_replaceable:
                    items[i] = ItemFactory(new_items.pop(), player)
                    if not new_items:
                        break
            else:
                logging.warning(
                    f"Not all upgrades put into Player{player}' item pool. Putting remaining items in Capacity Upgrade shop instead.")
                bombupgrades = sum(1 for item in new_items if 'Bomb Upgrade' in item)
                arrowupgrades = sum(1 for item in new_items if 'Arrow Upgrade' in item)
                if bombupgrades:
                    capacityshop.add_inventory(1, 'Bomb Upgrade (+5)', 100, bombupgrades)
                if arrowupgrades:
                    capacityshop.add_inventory(1, 'Arrow Upgrade (+5)', 100, arrowupgrades)
        else:
            for item in new_items:
                world.push_precollected(ItemFactory(item, player))

    if any(setting in option for setting in 'ipP'):
        shops = []
        upgrade_shops = []
        total_inventory = []
        for shop in world.shops:
            if shop.region.player == player:
                if shop.type == ShopType.UpgradeShop:
                    upgrade_shops.append(shop)
                elif shop.type == ShopType.Shop and not shop.locked:
                    shops.append(shop)
                    total_inventory.extend(shop.inventory)

        if 'p' in option:
            def price_adjust(price: int) -> int:
                # it is important that a base price of 0 always returns 0 as new price!
                adjust = 2 if price < 100 else 5
                return int((price / adjust) * (0.5 + world.random.random() * 1.5)) * adjust

            def adjust_item(item):
                if item:
                    item["price"] = price_adjust(item["price"])
                    item['replacement_price'] = price_adjust(item["price"])

            for item in total_inventory:
                adjust_item(item)
            for shop in upgrade_shops:
                for item in shop.inventory:
                    adjust_item(item)

        if 'P' in option:
            for item in total_inventory:
                price_to_funny_price(item, world, player)
            # Don't apply to upgrade shops
            # Upgrade shop is only one place, and will generally be too easy to
            # replenish hearts and bombs

        if 'i' in option:
            world.random.shuffle(total_inventory)

            i = 0
            for shop in shops:
                slots = shop.slots
                shop.inventory = total_inventory[i:i + slots]
                i += slots