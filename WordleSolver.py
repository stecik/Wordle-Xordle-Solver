from math import log2, inf
from random import choice
import time
import itertools


class WordleSolver:
    def __init__(self, word_length=5) -> None:
        self.possible_answers = self._load_words("wordle_dict.txt")
        self.all_words = self.possible_answers.copy()
        self.optimized_words = self.optimize_words(self.all_words)
        self.answers = list(self._load_words("wordle_answers.txt"))
        self.word_length = word_length
        self.number_of_colors = 3**self.word_length

    def _load_words(self, file):
        with open(file, "r", encoding="utf-8") as f:
            words = {line.strip() for line in f.readlines()}
        return words

    def number_to_triadic(self, num, siz=None):
        if siz is None:
            siz = 5
        triadic = [0] * siz
        for i in range(siz):
            triadic[i] = num % 3
            num //= 3
        return triadic

    def triadic_to_number(self, tri):
        result = 0
        for digit in tri[::-1]:
            result = result * 3 + digit
        return result

    def wordle_eval_num(self, word, possible_answer):
        possible_answer_set = set(possible_answer)
        result = [0] * 5
        for i in range(5):
            if word[i] == possible_answer[i]:
                result[i] = 2
            elif word[i] in possible_answer_set:
                result[i] = 1
        return result

    def count_by_word(self, word):
        result = [0] * (self.number_of_colors)
        for possible_answer in self.possible_answers:
            i = self.triadic_to_number(self.wordle_eval_num(word, possible_answer))
            result[i] += 1
        return result

    def plog(self, n):
        if n == 0:
            return 0
        return log2(n) * n / len(self.possible_answers)

    def cond_entropy(self, word):
        return sum(map(self.plog, self.count_by_word(word)))

    def next_word(self, word, color):
        number = self.triadic_to_number(color)
        possible_answers = self.get_possible_answers(word, number)
        self.possible_answers = possible_answers
        if len(self.possible_answers) == 1:
            return (list(self.possible_answers)[0], 0)
        in_possible_answers = set()
        not_in_possible_answers = set()
        min_ent = inf
        for word in self.optimized_words:
            cond_e = self.cond_entropy(word)
            if cond_e == min_ent:
                if word in self.possible_answers:
                    in_possible_answers.add((word, cond_e))
                else:
                    not_in_possible_answers.add((word, cond_e))
            elif cond_e < min_ent:
                in_possible_answers = set()
                not_in_possible_answers = set()
                min_ent = cond_e
                if word in self.possible_answers:
                    in_possible_answers.add((word, cond_e))
                else:
                    not_in_possible_answers.add((word, cond_e))

        if in_possible_answers:
            result = choice(list(in_possible_answers))
        else:
            result = choice(list(not_in_possible_answers))
        return result

    def get_possible_answers(self, word, number):
        possible_answers = set()
        for possible_answer in self.possible_answers:
            if (
                self.triadic_to_number(self.wordle_eval_num(word, possible_answer))
                == number
            ):
                possible_answers.add(possible_answer)
        return possible_answers

    def optimize_words_for_first(self, words):
        optimized_words = set()
        for w in words:
            w_set = set(w)
            if not len(w_set) == 5:
                continue
            if "e" != w[-1]:
                continue
            if "a" not in w_set:
                continue
            if "o" not in w_set:
                continue
            optimized_words.add(w)
        return optimized_words

    def optimize_words(self, words):
        optimized_words = set()
        for w in words:
            if not len(set(w)) == 5:
                continue
            optimized_words.add(w)
        optimized_words = self.get_repr_sample(optimized_words)
        return optimized_words

    def get_repr_sample(self, words):
        size = int(len(words) * 0.5)
        return set(itertools.islice(words, size))

    def get_first_word(self):
        self.possible_answers = self.answers
        min_ent = inf
        for word in self.optimize_words_for_first(self.all_words):
            cond_e = self.cond_entropy(word)
            if cond_e < min_ent:
                result = (word, cond_e)
                min_ent = cond_e
        self.possible_answers = self.all_words
        return result

    def get_second_words(self, first_word):
        temp = self.possible_answers.copy()
        self.all_words = self.optimized_words
        with open("second_words.txt", "w", encoding="utf-8") as f:
            colors = [self.number_to_triadic(x) for x in range(self.number_of_colors)]
            for color in colors:
                word, entropy = self.next_word(first_word, color)
                f.write(f"{word},{entropy}\n")
                self.possible_answers = temp.copy()

    def load_second_words(self):
        second_words = []
        with open("second_words.txt", "r", encoding="utf-8") as f:
            for line in f.readlines():
                word, entropy = line.strip().split(",")
                second_words.append((word, entropy))
        return second_words

    def input_mode(self):
        print("Input mode")
        print("Enter 2 for green letter, 1 for yellow letter, 0 for grey letter")
        print(
            "*****************************************************************************"
        )
        first_word = self.get_first_word()[0]
        print(f"Guess 1: {first_word}")
        color = self.get_user_color()
        if color == [2, 2, 2, 2, 2]:
            print(f"{first_word} is the answer!")
        else:
            self.possible_answers = self.get_possible_answers(
                first_word, self.triadic_to_number(color)
            )
            next_word = self.load_second_words()[self.triadic_to_number(color)][0]
            print(f"Guess 2: {next_word}")
            color = self.get_user_color()
            self.possible_answers = self.get_possible_answers(
                next_word, self.triadic_to_number(color)
            )
            attempt = 2
            while attempt <= 5:
                attempt += 1
                if len(self.possible_answers) == 1:
                    attempt += 1
                    print(f"{self.possible_answers[0]} is the answer!")
                    break
                next_word = self.next_word(next_word, color)[0]
                print(f"Guess {attempt}: {next_word}")
                color = self.get_user_color()

    def check_color_format(self, color):
        if len(color) != 5:
            return False
        for char in color:
            if char != 0 and char != 1 and char != 2:
                return False
        return True

    def get_user_color(self):
        color = list(map(int, list(input("Enter color in format 00000: "))))
        while not self.check_color_format(color):
            color = list(
                map(int, list(input("Wrong format. Enter color in format 00000: ")))
            )
        return color

    def test(self, n=1, answer=None):
        if answer is None:
            for i in range(n):
                answer = choice(self.answers)
                self.get_answer(answer)
        else:
            self.get_answer(answer)

    def get_answer(self, answer):
        attempt = 0
        print("answer: ", answer)
        first_word = self.get_first_word()[0]
        print(first_word)
        eval_num = self.triadic_to_number(self.wordle_eval_num(first_word, answer))
        attempt += 1
        if eval_num == self.triadic_to_number([2, 2, 2, 2, 2]):
            print(self.possible_answers, answer, attempt)
            return True
        self.possible_answers = self.get_possible_answers(first_word, eval_num)
        next_word = self.load_second_words()[eval_num][0]
        while attempt < 7:
            print(next_word)
            attempt += 1
            eval_num = self.triadic_to_number(self.wordle_eval_num(next_word, answer))
            if eval_num == self.triadic_to_number([2, 2, 2, 2, 2]):
                print(next_word, answer, attempt)
                return True
            next_word = self.next_word(next_word, self.number_to_triadic(eval_num))[0]
        print(answer, attempt, self.possible_answers)
        return False


if __name__ == "__main__":
    ws = WordleSolver()
    start = time.time()
    ws.test(10)
    end = time.time()
    print(f"time: {end - start}")

    # ws.input_mode()
