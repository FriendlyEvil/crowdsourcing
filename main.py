import json
import requests
import warnings
import csv
import pool

warnings.filterwarnings('ignore', message='Unverified HTTPS request')


def _make_url(url):
    return '{}/api/v1/{}'.format(HOST, url)


def _get(url):
    request = requests.get(_make_url(url), headers=HEADER, verify=False)
    request.raise_for_status()
    return request.json()


def _post(url, data={}):
    a = json.dumps(data)
    print(a)
    request = requests.post(_make_url(url), data=a, headers=HEADER, verify=False)
    return request.json()


def get_data_from_tsv(file_name):
    with open(file_name) as f:
        reader = csv.reader(f, delimiter='\t')
        return list(reader)


def create_task_from_file(pool_id, filename, overlap):
    return create_task_json(pool_id, get_data_from_tsv(filename), overlap)


def _read_project_spec_from_file(filename):
    with open(filename) as f:
        return json.load(f)


def create_project(filename):
    return _post("projects", _read_project_spec_from_file(filename))


def create_task_json(pool_id, tasks, overlap):
    headers = list(map(lambda h: h[h.find(':') + 1:], tasks[0]))
    return list(map(lambda task: {
        'pool_id': pool_id,
        'input_values': format_tasks_input(headers, task),
        'overlap': overlap,
        'infinite_overlap': False
    }, tasks[1:]))


def format_tasks_input(headers, task):
    return format_task(zip(headers, task))


def format_task(task):
    res = {}
    for t in task:
        res[t[0]] = t[1]
    return res


def create_task(pool_id, filename, overlap):
    return _post('tasks', create_task_from_file(pool_id, filename, overlap))


def get_project(project_id):
    return _get(f"projects/{project_id}")


def get_pool(pool_id):
    return _get(f"pools/{pool_id}")


def init(is_test):
    from const import init
    init(is_test)
    global HOST, HEADER
    from const import HOST, HEADER


def open_pool(pool_id):
    return _post("pools/{}/open".format(pool_id))


def create_pool(data):
    return _post("pools", data)


def aggregate(pool_id):
    a = json.dumps({"type": "DAWID_SKENE"})
    # api это пиздец
    request = requests.post(f"https://toloka.yandex.ru/api/new/aggregator/pools/{pool_id}/aggregate", data=a, headers=HEADER, verify=False)
    return request.json()


def operation_info(uid):
    return _get("operations/{}".format(uid))


def create_first_pool():
    data = {}
    pool.set_default_settings(data, 29901, "private name")
    pool.add_region_filters(data)
    pool.add_lang_filters(data)
    pool.set_mixer_config(data, 9, 1)
    pool.add_config(data, pool.create_config_headers("GOLDEN_SET"),
                    [pool.create_condition("total_answers_count", "GTE", 3),
                     pool.create_condition("correct_answers_rate", "LT", 60.0)],
                    pool.create_config_headers("RESTRICTION", {
                        "private_comment": "Ошибка на контрольных заданиях",
                        "scope": "PROJECT",
                        "duration_days": 10
                    }))
    pool.set_default_overlap_for_new_task_suites(data, 3)
    return data


def create_second_pool():
    data = {}
    pool.set_default_settings(data, 29901, "private name", auto_accept_solutions=False)
    pool.add_region_filters(data)
    pool.add_lang_filters(data)
    pool.add_config(data, pool.create_config_headers("ASSIGNMENTS_ASSESSMENT"),
                    [pool.create_condition("assessment_event", "EQ", "REJECT")],
                    pool.create_config_headers("CHANGE_OVERLAP", {
                        "delta": 1,
                        "open_pool": True
                    }))
    pool.add_config(data, pool.create_config_headers("ANSWER_COUNT"),
                    [pool.create_condition("assignments_accepted_count", "GTE", 1)],
                    pool.create_config_headers("SET_SKILL", {
                        "skill_id": "14721",
                        "skill_value": 1
                    }))
    pool.set_default_overlap_for_new_task_suites(data, 1)
    print(json.dumps(data))


def create_third_pool():
    data = {}
    pool.set_default_settings(data, 29901, "private name")
    pool.add_region_filters(data)
    pool.add_lang_filters(data)
    pool.add_skill_filter(data, "14721", "EQ", "")
    pool.add_config(data, pool.create_config_headers("MAJORITY_VOTE", {"answer_threshold": 2}),
                    [pool.create_condition("total_answers_count", "GTE", 10),
                     pool.create_condition("correct_answers_rate", "LT", 50.0)],
                    pool.create_config_headers("RESTRICTION", {
                        "private_comment": "Не совпадает с большинством",
                        "scope": "PROJECT",
                        "duration_days": 10
                    }))
    pool.set_default_overlap_for_new_task_suites(data, 3)
    print(json.dumps(data))


if __name__ == '__main__':
    init(False)
#   code
