from WordleSolver import WordleSolver
from string import ascii_lowercase
import heapq


class XordleSolver(WordleSolver):
    def __init__(self, word_length=5) -> None:
        super().__init__(word_length)
        self.letters = set(ascii_lowercase)
        self.known_letters = set()
        self.unknown_letters = set(ascii_lowercase)
        self.used_words = set()
        self.green = set()
        self.yellow = set()

    def check_disjunction(self, word1, word2):
        set1 = set(word1)
        set2 = set(word2)
        if len(set1.intersection(set2)) == 0:
            return True
        return False

    def find_disj_sets(self, word_list):
        disj_sets = set()
        for word in word_list:
            disj = set()
            found = False
            for word2 in word_list:
                if self.check_disjunction(word, word2):
                    disj.add(word2)
                    found = True
            if found:
                disj_sets.add((word, frozenset(disj)))
        return disj_sets

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
                self.yellow.add(word[i])
                for w in self.possible_answers:
                    if word[i] != w[i]:
                        possible_answers.add(w)
            elif color[i] == 2:
                self.unknown_letters.discard(word[i])
                self.known_letters.add(word[i])
                self.green.add(word[i])

    def find_next_word(self):
        heap = []
        for word in self.optimized_words:
            counter = 0
            for letter in word:
                if letter not in self.unknown_letters:
                    counter += 1
            if counter > 0:
                for w in self.used_words:
                    for i in range(self.word_length):
                        if w[i] == word[i]:
                            if w[i] in self.green:
                                counter += 2
                            else:
                                counter += 1
            heapq.heappush(heap, (counter, word))
        result = heapq.heappop(heap)
        self.used_words.add(result)
        return result

    def sort_from_best(self):
        pass

    def get_letter_freq(self):
        freq_table = {}
        for word in self.all_words:
            for letter in word:
                if letter in freq_table.keys():
                    freq_table[letter] += 1
                else:
                    freq_table[letter] = 1
        return sorted(freq_table.items(), key=lambda x: x[1])

    def find_optimal_word(self, disj_sets):
        pass


if __name__ == "__main__":
    xs = XordleSolver()
    xs.eliminate("truck", [0, 1, 0, 0, 0])
    print(len(xs.possible_answers))
    print(xs.find_next_word())
