def restart(arr, user_id):
    arr[user_id] = {'hp':100,'level': 1, 'xp': 0, 'balance': 0, 'inventory': [], 'farming':1, 'farming_xp':0, 'dmg' : 5, 'quests': [], 'kill_list': [], 'farm':[]}

async def add_to_inventory(name, character, n, level):
        m = False
        for item in character['inventory']:
            if item['name'] == name:
                item['count'] += n
                m = True
        if not m:
            item = {'name': name, 'count': n, 'level': level}
            character['inventory'].append(item)
        print('test')
        return character['inventory']