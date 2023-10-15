from math import log2, inf
import numpy as np
from random import choice
import time


class WordleSolver:
    def __init__(self, word_length=5) -> None:
        self.possible_answers = self._load_words("words.txt")
        self.all_words = self.possible_answers.copy()
        self.optimized_words = self.optimize_words(self.all_words)
        self.answers = self._load_words("answers.txt")
        self.word_length = word_length
        self.number_of_colors = 3**self.word_length

    def _load_words(self, file):
        with open(file, "r", encoding="utf-8") as f:
            words = [line.strip() for line in f.readlines()]
        return words

    def number_to_triadic(self, num, siz=None):
        if siz is None:
            siz = self.word_length
        if siz == 0:
            return []
        else:
            return [num % 3] + self.number_to_triadic(num // 3, siz - 1)

    def triadic_to_number(self, tri):
        if tri == []:
            return 0
        else:
            return 3 * self.triadic_to_number(tri[1:]) + tri[0]

    def wordle_eval_num(self, word, possible_answer):
        result = [0] * 5
        for i in range(5):
            if word[i] == possible_answer[i]:
                result[i] = 2
            elif possible_answer.find(word[i]) >= 0:
                result[i] = 1
        return self.triadic_to_number(result)

    def count_by_word(self, word):
        result = [0] * (3**5)
        for possible_answer in self.possible_answers:
            i = self.wordle_eval_num(word, possible_answer)
            result[i] += 1
        return result

    def plog(self, n):
        if n == 0:
            return 0
        return log2(n) * n / len(self.possible_answers)

    def cond_entropy(self, word):
        return sum(map(self.plog, self.count_by_word(word)))

    def next_word(self, word, color, entropy_value=0):
        number = self.triadic_to_number(color)
        possible_answers = self.get_possible_answers(word, number)
        self.possible_answers = possible_answers
        if entropy_value == 0:
            result = None
            min_ent = inf
            for word in self.all_words:
                cond_e = self.cond_entropy(word)
                if cond_e < min_ent:
                    result = (word, cond_e)
                    min_ent = cond_e
        else:
            for word in self.all_words:
                cond_e = self.cond_entropy(word)
                if cond_e < entropy_value:
                    result = (word, cond_e)
                    break
        return result

    def get_possible_answers(self, word, number):
        possible_answers = []
        for possible_answer in self.possible_answers:
            if self.wordle_eval_num(word, possible_answer) == number:
                possible_answers.append(possible_answer)
        return possible_answers

    def optimize_words_for_first(self, words):
        optimized_words = []
        for w in words:
            if not len(set(w)) == 5:
                continue
            if "a" not in w:
                continue
            if "o" not in w:
                continue
            if "e" != w[-1]:
                continue
            optimized_words.append(w)
        return optimized_words

    def optimize_words(self, words):
        optimized_words = []
        for w in words:
            if not len(set(w)) == 5:
                continue
            optimized_words.append(w)
        return optimized_words

    def get_first_word(self, entropy_value=0):
        self.possible_answers = self.answers
        if entropy_value == 0:
            result = None
            min_ent = inf
            for word in self.optimize_words_for_first(self.all_words):
                cond_e = self.cond_entropy(word)
                if cond_e < min_ent:
                    result = (word, cond_e)
                    min_ent = cond_e
        else:
            for word in self.optimize_words_for_first(self.all_words):
                cond_e = self.cond_entropy(word)
                if cond_e < entropy_value:
                    result = (word, cond_e)
                    break
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
            while attempt < 7:
                attempt += 1
                if len(self.possible_answers) == 1:
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

    def test(self, n, answer=None):
        if answer is None:
            random_choice = True
        else:
            n = 1
            random_choice = False
        for i in range(n):
            if random_choice:
                answer = choice(self.answers)
            print("answer: ", answer)
            first_word = self.get_first_word()[0]
            print(first_word)
            self.possible_answers = self.get_possible_answers(
                first_word, self.wordle_eval_num(first_word, answer)
            )
            next_word = self.load_second_words()[
                self.wordle_eval_num(first_word, answer)
            ][0]
            attempt = 2
            success = False
            print(next_word)
            while attempt <= 7:
                attempt += 1
                next_word = self.next_word(
                    next_word,
                    self.number_to_triadic(self.wordle_eval_num(next_word, answer)),
                )[0]
                print(next_word)
                if len(self.possible_answers) == 1:
                    print(self.possible_answers[0], answer, attempt)
                    success = True
                    break
            if not success:
                print(answer, attempt, self.possible_answers)


if __name__ == "__main__":
    ws = WordleSolver()
    # ws.input_mode()
    start = time.time()
    ws.test(100)
    end = time.time()
    print(f"time: {end - start}")
