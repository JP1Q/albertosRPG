def level_up(character):
    if character['xp'] > character['level'] * 250 * character['level']/10:
        return 1
    else:
        return 0
    
def farm_level_up(character):
    if character['farming_xp'] > 100 * character['farming']:
        return 1
    else:
        return 0