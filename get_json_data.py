import json


def get_json_data(file):
    with open(file, "r") as f:
        data = json.load(f)
        return data


def save_to_txt(file, data):
    with open(file, "w") as f:
        for item in data:
            if "*" in set(item):
                continue
            f.write(f"{item}\n")


if __name__ == "__main__":
    data = get_json_data("fives_targets.json")
    save_to_txt("xordle_answers.txt", data)
