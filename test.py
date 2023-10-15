def number_to_triadic(num, siz=None):
    if siz is None:
        siz = 5
    triadic = [0] * siz
    for i in range(siz):
        triadic[i] = num % 3
        num //= 3
    return triadic


def triadic_to_number(tri):
    result = 0
    for digit in tri[::-1]:
        result = result * 3 + digit
    return result


def wordle_eval_num(word, possible_answer):
    possible_answer_set = set(possible_answer)
    result = [0] * 5
    for i in range(5):
        if word[i] == possible_answer[i]:
            result[i] = 2
        elif word[i] in possible_answer_set:
            result[i] = 1
    return result


def wordle_eval_num2(word, possible_answer):
    result = [0] * 5
    for i in range(5):
        if word[i] == possible_answer[i]:
            result[i] = 2
        elif possible_answer.find(word[i]) >= 0:
            result[i] = 1
    return result


print(wordle_eval_num("hello", "hares"))
print(wordle_eval_num2("hello", "hares"))
