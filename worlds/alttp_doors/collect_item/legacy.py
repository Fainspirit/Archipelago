from BaseClasses import CollectionState, Item


def collect_item(world, state: CollectionState, item: Item, remove=False):
    item_name = item.name
    if item_name.startswith('Progressive '):
        if remove:
            if 'Sword' in item_name:
                if state.has('Golden Sword', item.player):
                    return 'Golden Sword'
                elif state.has('Tempered Sword', item.player):
                    return 'Tempered Sword'
                elif state.has('Master Sword', item.player):
                    return 'Master Sword'
                elif state.has('Fighter Sword', item.player):
                    return 'Fighter Sword'
                else:
                    return None
            elif 'Glove' in item.name:
                if state.has('Titans Mitts', item.player):
                    return 'Titans Mitts'
                elif state.has('Power Glove', item.player):
                    return 'Power Glove'
                else:
                    return None
            elif 'Shield' in item_name:
                if state.has('Mirror Shield', item.player):
                    return 'Mirror Shield'
                elif state.has('Red Shield', item.player):
                    return 'Red Shield'
                elif state.has('Blue Shield', item.player):
                    return 'Blue Shield'
                else:
                    return None
            elif 'Bow' in item_name:
                if state.has('Silver Bow', item.player):
                    return 'Silver Bow'
                elif state.has('Bow', item.player):
                    return 'Bow'
                else:
                    return None
        else:
            if 'Sword' in item_name:
                if state.has('Golden Sword', item.player):
                    pass
                elif state.has('Tempered Sword', item.player) and world.difficulty_requirements[
                    item.player].progressive_sword_limit >= 4:
                    return 'Golden Sword'
                elif state.has('Master Sword', item.player) and world.difficulty_requirements[
                    item.player].progressive_sword_limit >= 3:
                    return 'Tempered Sword'
                elif state.has('Fighter Sword', item.player) and world.difficulty_requirements[
                    item.player].progressive_sword_limit >= 2:
                    return 'Master Sword'
                elif world.difficulty_requirements[item.player].progressive_sword_limit >= 1:
                    return 'Fighter Sword'
            elif 'Glove' in item_name:
                if state.has('Titans Mitts', item.player):
                    return
                elif state.has('Power Glove', item.player):
                    return 'Titans Mitts'
                else:
                    return 'Power Glove'
            elif 'Shield' in item_name:
                if state.has('Mirror Shield', item.player):
                    return
                elif state.has('Red Shield', item.player) and world.difficulty_requirements[
                    item.player].progressive_shield_limit >= 3:
                    return 'Mirror Shield'
                elif state.has('Blue Shield', item.player) and world.difficulty_requirements[
                    item.player].progressive_shield_limit >= 2:
                    return 'Red Shield'
                elif world.difficulty_requirements[item.player].progressive_shield_limit >= 1:
                    return 'Blue Shield'
            elif 'Bow' in item_name:
                if state.has('Silver Bow', item.player):
                    return
                elif state.has('Bow', item.player) and (
                        world.difficulty_requirements[item.player].progressive_bow_limit >= 2
                        or world.logic[item.player] == 'noglitches'
                        or world.swordless[
                            item.player]):  # modes where silver bow is always required for ganon
                    return 'Silver Bow'
                elif world.difficulty_requirements[item.player].progressive_bow_limit >= 1:
                    return 'Bow'
    elif item.advancement:
        return item_name