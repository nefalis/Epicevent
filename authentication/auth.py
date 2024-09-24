current_user = None


def is_authenticated():
    return current_user is not None


def login(user):
    global current_user
    current_user = user


def logout():
    global current_user
    current_user = None


def get_current_user():
    return current_user
