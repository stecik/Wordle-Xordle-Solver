def find_disj_tuples(l):
    d = set()
    for word in l:
        for word2 in l:
            if check_disjunction(word, word2):
                print(word, word2)
                d.add((word, word2))
    print(d)


def check_disjunction(word1, word2):
    set1 = set(word1)
    set2 = set(word2)
    if set1.intersection(set2):
        return False
    return True


l = {"abaca", "vogue"}
find_disj_tuples(l)
