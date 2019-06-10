def player_group(user):
    if user:
        return user.groups.filter(name='Players').exists()
    return False


def is_manager(user):
    if user.username == "siteadmin":
        return True
    else:
        return False
