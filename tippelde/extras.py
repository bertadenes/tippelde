def player_group(user):
    if user:
        return user.groups.filter(name='Players').exists()
    return False


def is_manager(user):
    if user.username == "siteadmin":
        return True
    else:
        return False


def ev(h_goals, a_goals, h_guess, a_guess):
    if h_goals == a_goals and h_guess != a_guess:
        return 0
    # elif h_goals != a_goals and (h_goals - a_goals) * (h_guess - a_guess) <= 0:
    #     return 0
    elif h_goals > a_goals and h_guess <= a_guess:
        return 0
    elif h_goals < a_goals and h_guess >= a_guess:
        return 0
    if h_goals - a_goals == h_guess - a_guess:
        if h_goals == h_guess:
            return 25
        return 22 - 2 * abs(h_goals - h_guess)
    return 10
