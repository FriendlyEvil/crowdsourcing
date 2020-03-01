HOST, HEADER, _TOKEN_PATH_PATTERN = None, None, "/home/friendlyevil/university/crayd/{}"


def _get_token(path):
    with open(path) as f:
        return f.readline()


def init(is_test):
    global HOST, HEADER
    if is_test:
        HOST = "https://sandbox.toloka.yandex.ru"
        TOKEN_PATH = _TOKEN_PATH_PATTERN.format(".sandbox_token")
    else:
        HOST = "https://toloka.yandex.ru"
        TOKEN_PATH = _TOKEN_PATH_PATTERN.format(".token")
    HEADER = {"Content-Type": "application/json", "Authorization": "OAuth " + _get_token(TOKEN_PATH)}
