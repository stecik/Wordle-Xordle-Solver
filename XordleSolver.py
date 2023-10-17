from WordleSolver import WordleSolver
from string import ascii_lowercase
import heapq


class XordleSolver(WordleSolver):
    def __init__(self, word_length=5) -> None:
        super().__init__(word_length)
        self.possible_answers = self._load_words("xordle_answers.txt")
        self.all_words = self._load_words("xordle_dict.txt")
        self.optimized_words = self.optimize_words(self.all_words)
        self.answers = self.possible_answers.copy()
        self.disj_tuples = set()
        self.letters = set(ascii_lowercase)
        self.known_letters = set()
        self.unknown_letters = set(ascii_lowercase)
        self.used_words = set()
        self.greens = set()
        self.yellows = set()

    def check_disjunction(self, word1, word2):
        set1 = set(word1)
        set2 = set(word2)
        if len(set1.intersection(set2)) == 0:
            return True
        return False

    def find_disj_tuples(self):
        for word in self.possible_answers:
            for word2 in self.possible_answers:
                if self.check_disjunction(word, word2):
                    self.disj_tuples.add((word, word2))

    def eliminate(self, word, color):
        for i in range(self.word_length):
            possible_answers = set()
            if color[i] == 0:
                self.unknown_letters.discard(word[i])
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
        result = heapq.heappop(heap)
        self.used_words.add(result[1])
        return result

    def get_letter_freq(self):
        freq_table = {}
        for word in self.all_words:
            for letter in word:
                if letter in freq_table.keys():
                    freq_table[letter] += 1
                else:
                    freq_table[letter] = 1
        return sorted(freq_table.items(), key=lambda x: x[1])

    def remove_multiple_letters(self):
        new_disj_tuples = set()
        letters_len = len(self.known_letters)
        for tpl in self.disj_tuples:
            if not len(self.unknown_letters):
                if len(set(tpl[0]).union(set(tpl[1]))) == letters_len:
                    new_disj_tuples.add(tpl)
            else:
                if len(set(tpl[0]).union(set(tpl[1]))) >= letters_len:
                    new_disj_tuples.add(tpl)

        self.disj_tuples = new_disj_tuples

    def remove_by_green(self):
        old_disj_tuples = self.disj_tuples.copy()
        for green in self.greens:
            new_disj_tuples = set()
            for tpl in self.disj_tuples:
                if tpl[0][green[1]] == green[0]:
                    new_disj_tuples.add(tpl)
            if len(old_disj_tuples) > len(new_disj_tuples):
                old_disj_tuples = new_disj_tuples
        self.disj_tuples = old_disj_tuples

    def remove_by_yellow(self):
        old_disj_tuples = self.disj_tuples.copy()
        for yellow in self.yellows:
            for tpl in self.disj_tuples:
                if tpl[0][yellow[1]] == yellow[0] or tpl[1][yellow[1]] == yellow[0]:
                    old_disj_tuples.discard(tpl)
        self.disj_tuples = old_disj_tuples

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
        self.find_disj_tuples()
        self.remove_multiple_letters()
        self.remove_by_green()
        self.remove_by_yellow()

    def input_mode(self):
        print("Input mode")
        print("Enter 2 for green letter, 1 for yellow letter, 0 for grey letter")
        print(
            "*****************************************************************************"
        )
        initial_word = input("Enter revealed word: ").lower().strip()
        self.used_words.add(initial_word)
        self.eliminate(initial_word, self.get_user_color())
        attempt = 0
        while attempt < 6:
            attempt += 1
            next_word = self.find_next_word()[1]
            print(f"Next word: {next_word}")
            self.eliminate(next_word, self.get_user_color())
        self.eliminate_disj_tuples()
        if len(self.disj_tuples) == 1:
            print(f"Answers are: {self.disj_tuples}")
        else:
            next_word = self.get_most_frequent()
            print(f"Next word: {next_word}")
            self.eliminate(next_word, self.get_user_color())
            self.eliminate_disj_tuples()
        print(f"Answers are: {self.disj_tuples}")


if __name__ == "__main__":
    xs = XordleSolver()
    xs.input_mode()
