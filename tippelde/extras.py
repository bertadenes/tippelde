def player_group(user):
    if user:
        return user.groups.filter(name='Players').exists()
    return False
