import math
import time
from random import choice, randint

words = []
all_words = []

with open("words.txt", "r", encoding="utf-8") as f:
    words = [line.strip() for line in f.readlines()]
    all_words = words.copy()

with open("answers.txt", "r", encoding="utf-8") as f:
    previous_answers = [x.strip() for x in f.readlines()]


def number_to_triadic(num, siz=5):
    if siz == 0:
        return []
    else:
        return [num % 3] + number_to_triadic(num // 3, siz - 1)


def triadic_to_number(tri):
    if tri == []:
        return 0
    else:
        return 3 * triadic_to_number(tri[1:]) + tri[0]


def wordle_eval_num(y, sw):
    res = [0] * 5
    for i in range(5):
        if y[i] == sw[i]:
            res[i] = 2
        elif sw.find(y[i]) >= 0:
            res[i] = 1
    return triadic_to_number(res)


def count_by_word(y):
    res = [0] * (3**5)
    for sw in words:
        i = wordle_eval_num(y, sw)
        res[i] += 1
    return res


def plog(n):
    if n == 0:
        return 0
    return math.log2(n) * n / len(words)


def cond_entropy(y):
    return sum(map(plog, count_by_word(y)))


# def next_word(w, col, entropy_value=0):
#     global words
#     dist = distribute_by_word(w)
#     words = dist[triadic_to_number(col)]
#     if entropy_value == 0:
#         result = [(w, cond_entropy(w)) for w in all_words]
#     else:
#         for w in words:
#             cond_e = cond_entropy(w)
#             if cond_e < entropy_value:
#                 result = (w, cond_e)
#                 break

#     result.sort(key=lambda x: x[1])
#     min_ent = result[0][1]
#     i = 0
#     while min_ent == result[i][1]:
#         if result[i][0] in words:
#             return result[i]
#         else:
#             i += 1
#     return result[0]


def next_word(w, col, entropy_value=0):
    global words
    dist = distribute_by_word(w, col)
    words = dist
    if entropy_value == 0:
        result = None
        min_ent = math.inf
        for w in all_words:
            cond_e = cond_entropy(w)
            if cond_e < min_ent:
                result = (w, cond_e)
                min_ent = cond_e
    else:
        for w in all_words:
            cond_e = cond_entropy(w)

            if cond_e < entropy_value:
                result = (w, cond_e)
                break
    return result


def distribute_by_word(w, col):
    dist = []
    hash = triadic_to_number(col)
    for sw in words:
        if wordle_eval_num(w, sw) == hash:
            dist.append(sw)
    return dist


def get_first_word(entropy_value=0.0):
    if entropy_value == 0.0:
        result = None
        min_ent = math.inf
        for w in optimize_words_for_first():
            cond_e = cond_entropy(w)
            if cond_e < min_ent:
                result = (w, cond_e)
                min_ent = cond_e
    else:
        for w in optimize_words_for_first():
            cond_e = cond_entropy(w)
            if cond_e < entropy_value:
                result = (w, cond_e)
                break
    return result


def optimize_words_for_first():
    optimized_words = []
    for w in words:
        if not len(set(w)) == 5:
            continue
        if "a" not in w:
            continue
        if "e" not in w:
            continue
        if "s" != w[-1]:
            continue
        optimized_words.append(w)
    return optimized_words


def optimize_words():
    optimized_words = []
    for w in words:
        if not len(set(w)) == 5:
            continue
        optimized_words.append(w)
    return optimized_words


def get_optimal_entropy_for_second_word(word):
    global words
    global all_words
    all_words = optimize_words()
    words_complete = words.copy()
    with open("optimal_entropy_tares.txt", "w", encoding="utf-8") as f:
        colors = [number_to_triadic(x) for x in range(243)]
        for col in colors:
            next = next_word(word, col)
            print(next)
            f.write(f"{next}\n")
            words = words_complete.copy()


def test(n, entropy_value=0.0, answer=None, random_choice=True):
    if answer is None:
        with open("answers.txt", "r", encoding="utf-8") as f:
            answers = [line.strip() for line in f.readlines()]
            random_choice = True
    else:
        n = 1
        random_choice = False
    global words
    for i in range(n):
        attempt = 0
        if random_choice:
            answer = choice(answers)
        print("answer: ", answer)
        word = "tares"
        # word = get_first_word(entropy_value)[0]
        while attempt <= 6 and len(words) > 1:
            attempt += 1
            col = number_to_triadic(wordle_eval_num(word, answer))
            next = next_word(word, col)
            word = next[0]
            if next[1] < 0.0:
                print(words[0], answer, attempt)
        if len(word) > 1:
            print(words, answer, attempt)
        words = all_words.copy()


if __name__ == "__main__":
    # 1 word e < 8.1 ("panes") (time: 0.84) (word order: 93)
    # start = time.time()
    # test(1, 8.1)
    # end = time.time()
    # print("time: ", end - start)
    # get_optimal_entropy_for_second_word("tares")
    # col = randint(0, 242)
    # col = triadic_to_number([1, 1, 0, 1, 0])
    # second_words = []
    # with open("optimal_entropy_tares.txt", "r", encoding="utf-8") as f:
    #     second_words = [line.strip() for line in f.readlines()]

    # next = next_word("tares", number_to_triadic(col))
    # second = second_words[col]

    # print(next, second)

    # next = next_word("leant", [0, 1, 1, 2, 2])
    # print(next)
    # next = next_word("might", [0, 0, 1, 0, 2])
    # print(words)
    test(1, answer="stone")
