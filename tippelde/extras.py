def player_group(user):
    if user:
        return user.groups.filter(name='Players').exists()
    return False


def is_manager(user):
    if user.username == "guber" or user.username == "berta":
        return True
    else:
        return False


def ev(h_goals, a_goals, h_guess, a_guess):
    if h_goals == a_goals and h_guess != a_guess:
        return 0
    elif h_goals != a_goals and (h_goals - a_goals) * (h_guess - a_guess) <= 0:
        return 0
    if h_goals - a_goals == h_guess - a_guess:
        if h_goals == h_guess:
            return 25
        points = 22 - 2 * abs(h_goals - h_guess)
        if points < 0:
            return 0
        else:
            return points
    else:
        mistake = abs(abs(h_goals-a_goals) - abs(h_guess-a_guess))
        points = 20 - 3 * mistake
        if points < 0:
            return 0
        else:
            return points
