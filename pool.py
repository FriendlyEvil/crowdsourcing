import datetime


def _get_next_year_date():
    time = datetime.datetime.now() + datetime.timedelta(days=365)
    return time.strftime("%Y-%m-%dT%H:%M:%S.%f")


def set_default_settings(data, project_id, private_name, may_contain_adult_content=True,
                         reward_per_assignment=0.01, assignment_max_duration_seconds=600, auto_accept_solutions=True):
    data.update({
        "project_id": str(project_id),
        "private_name": private_name,
        "may_contain_adult_content": may_contain_adult_content,
        "will_expire": _get_next_year_date(),
        "reward_per_assignment": reward_per_assignment,
        "assignment_max_duration_seconds": assignment_max_duration_seconds,
        "auto_accept_solutions": auto_accept_solutions
    })


def set_custom_date(data, date):
    data["will_expire"] = date


def set_mixer_config(data, real, golden, training=0):
    data.update({
        "mixer_config": {
            "real_tasks_count": real,
            "golden_tasks_count": golden,
            "training_tasks_count": training
        }
    })


# ---------------------create filters--------------------------------------------------------------


def create_condition(key, operator, value):
    return {
        "key": key,
        "operator": operator,
        "value": value
    }


def create_filter_condition(category, key, operator, value):
    condition = create_condition(key, operator, value)
    condition["category"] = category
    return condition


def _create_region_filter(region_id):
    return create_filter_condition("computed", "region_by_phone", "IN", region_id)


def _create_lang_filter(lang):
    return create_filter_condition("profile", "languages", "IN", lang)


# ---------------------------add filters--------------------------------------------------------------


def _add_filter(data, filter):
    temp = data.get("filter", {"and": []})
    temp["and"].append(filter)
    data["filter"] = temp


def add_skill_filter(data, key, operator, value=""):
    _add_filter(data, {
        "or": [create_filter_condition("skill", key, operator, value)]
    })


def add_region_filters(data, region_ids=[225, 187, 159, 149]):
    _add_filter(data, {
        "or": [_create_region_filter(i) for i in region_ids]
    })


def add_lang_filters(data, langs=["RU"]):
    _add_filter(data, {
        "or": [_create_lang_filter(i) for i in langs]
    })


# ---------------------------quality controls-------------------------------------------------------


def _add_quality_control_config(data, config):
    quality_control = data.get("quality_control", {"configs": []})
    quality_control["configs"].append(config)
    data["quality_control"] = quality_control


def create_config_headers(type, parameters={}):
    return {
        "type": type,
        "parameters": parameters
    }


def _create_action(type, parameters={}):
    return {"action": create_config_headers(type, parameters)}


def add_config(data, header_config, conditions, action):
    _add_quality_control_config(data, {
        "collector_config": header_config,
        "rules": [{
            "conditions": conditions,
            "action": action
        }]
    })


# ------------------------------defaults-----------------------------------------------------------------


def _add_default_property(data, name, value):
    temp = data.get("defaults", {})
    temp[name] = value
    data["defaults"] = temp


def set_default_overlap_for_new_task_suites(data, value):
    _add_default_property(data, "default_overlap_for_new_task_suites", value)
