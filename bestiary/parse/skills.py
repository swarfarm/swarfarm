from bestiary.parse import game_data


def skills():
    for master_id, raw in game_data.tables.SKILLS.items():
        print(master_id)



def homonculus_skills():
    pass
