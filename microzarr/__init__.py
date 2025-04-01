import json

DIR_NAME=__file__.rsplit("/", 1)[0]

def read_json_resource(name: str):
    return read_json(f"{DIR_NAME}/{name}")


def read_json(name: str):
    with open(name, "r", encoding="utf-8") as file:
        return json.load(file)
