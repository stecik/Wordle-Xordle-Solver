from WordleSolver import WordleSolver
from string import ascii_lowercase
import heapq
from itertools import combinations
from math import inf


class XordleSolver(WordleSolver):
    def __init__(self, word_length=5) -> None:
        super().__init__(word_length)
        self.possible_answers = self._load_words("xordle_dict.txt")
        self.all_words = self._load_words("xordle_dict.txt")
        self.optimized_words = self.get_repr_sample(self.optimize_words(self.all_words))
        self.answers = self.possible_answers.copy()
        self.disj_tuples = set()
        self.next_word_heap = [0]

        self.letters = set(ascii_lowercase)
        self.known_letters = set()
        self.unknown_letters = set(ascii_lowercase)
        self.used_words = set()
        self.greens = set()
        self.yellows = set()

    def count_by_word(self, word):
        result = [0] * (self.number_of_colors)
        for tpl in self.disj_tuples:
            merged_eval = self.merge_eval(
                self.wordle_eval_num(word, tpl[0]), self.wordle_eval_num(word, tpl[1])
            )
            i = self.triadic_to_number(merged_eval)
            result[i] += 1
        return result

    def merge_eval(self, eval1, eval2):
        result = []
        for i in range(self.word_length):
            if eval1[i] == 2 or eval2[i] == 2:
                result.append(2)
            elif eval1[i] == 1 or eval2[i] == 1:
                result.append(1)
            else:
                result.append(0)
        return result

    def check_disjunction(self, word1, word2):
        set1 = set(word1)
        set2 = set(word2)
        if set1.intersection(set2):
            return False
        return True

    def find_disj_tuples(self):
        disj_tuples = set()
        for word in self.possible_answers:
            for word2 in self.possible_answers:
                if self.check_disjunction(word, word2):
                    disj_tuples.add((word, word2))
        self.disj_tuples = disj_tuples

    def check_duplicate(self, index, word, color):
        for i in range(self.word_length):
            if (word[index] == word[i]) and (color[index] != color[i]):
                return True
        return False

    def eliminate(self, word, color):
        self.used_words.add(word)
        for i in range(self.word_length):
            possible_answers = set()
            if color[i] == 0:
                self.unknown_letters.discard(word[i])
                if not self.check_duplicate(i, word, color):
                    for w in self.possible_answers:
                        if word[i] not in set(w):
                            possible_answers.add(w)
                    self.possible_answers = possible_answers
            elif color[i] == 1:
                self.unknown_letters.discard(word[i])
                self.known_letters.add(word[i])
                self.yellows.add((word[i], i))
                for w in self.possible_answers:
                    if word[i] != w[i]:
                        possible_answers.add(w)
                self.possible_answers = possible_answers
            elif color[i] == 2:
                self.unknown_letters.discard(word[i])
                self.known_letters.add(word[i])
                self.greens.add((word[i], i))

    def find_next_word(self):
        heap = []
        for word in self.optimized_words:
            counter = 0
            for letter in word:
                if letter not in self.unknown_letters:
                    if letter in self.greens:
                        counter += 5
                    counter += 1
            if counter > 0:
                for w in self.used_words:
                    for i in range(self.word_length):
                        if w[i] == word[i]:
                            if w[i] in self.greens:
                                counter += 5
                            else:
                                counter += 1
            heapq.heappush(heap, (counter, word))
        self.next_word_heap = heap

    def find_next_word2(self):
        heap = []
        for word in self.possible_answers:
            cond_e = self.cond_entropy(word)
            heapq.heappush(heap, (cond_e, word))
        self.next_word_heap = heap

    def remove_multiple_letters(self):
        new_disj_tuples = set()
        possible_answers = set()
        letters_len = len(self.known_letters)
        for tpl in self.disj_tuples:
            if not self.unknown_letters:
                if len(set(tpl[0]).union(set(tpl[1]))) == letters_len:
                    new_disj_tuples.add(tpl)
                    possible_answers.add(tpl[0])
                    possible_answers.add(tpl[1])
            else:
                if len(set(tpl[0]).union(set(tpl[1]))) >= letters_len:
                    new_disj_tuples.add(tpl)
                    possible_answers.add(tpl[0])
                    possible_answers.add(tpl[1])
        self.disj_tuples = new_disj_tuples
        self.possible_answers = possible_answers

    def remove_by_green(self):
        if self.greens:
            comb = self.find_all_combinations()
            result = set()
            for c in comb:
                s1, s2 = c[0], c[1]
                for tpl in self.disj_tuples:
                    if self.validate_word_for_green(
                        tpl[0], s1
                    ) and self.validate_word_for_green(tpl[1], s2):
                        result.add(tpl[0])
                        result.add(tpl[1])
            self.possible_answers = result

    def validate_word_for_green(self, word, s):
        for tpl in s:
            if word[tpl[1]] != tpl[0]:
                return False
        return True

    def disj_tuples_to_set(self):
        possible_answers = set()
        for tpl in self.disj_tuples:
            possible_answers.add(tpl[0])
            possible_answers.add(tpl[1])
        self.possible_answers = possible_answers

    def validate_set(self, s):
        positions = [t[1] for t in s]
        return len(positions) == len(set(positions))

    def find_all_combinations(self):
        result = []
        for i in range(len(self.greens) + 1):
            for first_set in combinations(self.greens, i):
                second_set = self.greens - set(first_set)
                if self.validate_set(first_set) and self.validate_set(second_set):
                    result.append((set(first_set), second_set))
        return result

    def get_most_frequent(self):
        freq_table = dict()
        for tpl in self.disj_tuples:
            if tpl[0] in freq_table.keys():
                freq_table[tpl[0]] += 1
            else:
                freq_table[tpl[0]] = 1
            if tpl[1] in freq_table.keys():
                freq_table[tpl[1]] += 1
            else:
                freq_table[tpl[1]] = 1
        return sorted(freq_table.items(), key=lambda x: x[1])[-1][0]

    def eliminate_disj_tuples(self):
        if self.greens or len(self.known_letters) >= 5:
            self.find_disj_tuples()
            self.remove_multiple_letters()
            self.remove_by_green()

    def get_next_word(self):
        next_word = None
        if self.next_word_heap:
            next_word = heapq.heappop(self.next_word_heap)[1]
        while next_word in self.used_words and self.next_word_heap:
            next_word = heapq.heappop(self.next_word_heap)[1]
        return next_word

    def input_mode(self, method_acc=200, disj_acc=3000):
        print("Input mode")
        print("Enter 2 for green letter, 1 for yellow letter, 0 for grey letter")
        print(
            "*****************************************************************************"
        )
        initial_word = input("Enter revealed word: ").lower().strip()
        self.used_words.add(initial_word)
        guessed = 0
        color = self.get_user_color()
        self.eliminate(initial_word, color)
        if color == [2, 2, 2, 2, 2]:
            guessed += 1
        if len(self.possible_answers) <= disj_acc:
            self.eliminate_disj_tuples()
        attempt = 0

        while attempt < 8:
            if self.check_win():
                return True
            attempt += 1
            print(len(self.possible_answers))
            if len(self.possible_answers) >= method_acc:
                self.find_next_word()
            else:
                self.find_next_word2()
            next_word = self.get_next_word()
            print(f"Next word: {next_word}")
            color = self.get_user_color()
            if color == [2, 2, 2, 2, 2]:
                guessed += 1
                if self.check_win(guessed):
                    return True
            self.eliminate(next_word, color)
            if len(self.possible_answers) <= disj_acc:
                self.eliminate_disj_tuples()
        if self.check_win():
            return True
        print(f"You lose! Possible answers are: {self.disj_tuples}")
        return False

    def check_win(self, guessed=0):
        if guessed == 2:
            print("You win!")
            return True
        elif len(self.possible_answers) == 0:
            print("No answers found, check your color inputs")
            return False


if __name__ == "__main__":
    xs = XordleSolver()
    xs.input_mode()
