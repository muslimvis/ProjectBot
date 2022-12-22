# import config
import json


# def get_current_state(user_id):
#     with Vedis(config.db_file) as db:
#         try:
#             return db[user_id].decode()
#         except KeyError:
#             return config.States.S_START.value
#
#
# def set_state(user_id, value):
#     with Vedis(config.db_file) as db:
#         try:
#             db[user_id] = value
#             return True
#         except:
#             return False


def set_state_j(user_id, value):
    with open('json_states.json', 'w+') as fp:
        try:
            json_states = {user_id: value}
            json.dump(json_states, fp)
            return True
        except:
            return False


def get_current_state_j(key):
    with open('json_states.json', 'r') as fp:
        try:
            data = json.loads(fp.read())
            return data[key]
        except:
            return False


def set_json_data(key, value):
    with open('json_data.json', 'w+') as fp:
        try:
            json_data = {key: value}
            json.dump(json_data, fp)
            return True
        except:
            return False

def get_json_data(key):
    with open('json_data.json', 'r') as fp:
        try:
            data = json.loads(fp.read())
            return data[key]
        except:
            return False
