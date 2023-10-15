def load_from_raw(file):
    with open(file, "r", encoding="utf-8") as f:
        words = []
        for line in f.readlines():
            word_list = line.strip().lower().split(" ")
            words.extend(word_list)
    return words


def save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        for word in data:
            f.write(f"{word}\n")


words = load_from_raw("answers_raw.txt")

save("answers.txt", words)
