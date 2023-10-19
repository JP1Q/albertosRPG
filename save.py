import pickle

def save_quest_data(QUEST_DATA_FILE, quest_data):
    with open(QUEST_DATA_FILE, 'wb') as file:
        pickle.dump(quest_data, file)

def save_monster_data(MONSTER_DATA_FILE, monster_data):
    with open(MONSTER_DATA_FILE, 'wb') as file:
        pickle.dump(monster_data, file)

def save_character_data(CHARACTER_DATA_FILE, character_data):
    with open(CHARACTER_DATA_FILE, 'wb') as file:
        pickle.dump(character_data, file)

def save_shop_data(SHOP_DATA_FILE, shop_data):
    with open(SHOP_DATA_FILE, 'wb') as file:
        pickle.dump(shop_data,file)

def save_boss_data(BOSS_DATA_FILE, boss_data):
    with open(BOSS_DATA_FILE, 'wb') as file:
        pickle.dump(boss_data, file)

def save_moderators(MODERATORS_DATA_FILE, moderator_data):
    with open(MODERATORS_DATA_FILE, "wb") as f:
        pickle.dump(moderator_data, f)