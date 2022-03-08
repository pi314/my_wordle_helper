import math
import random

from itertools import product

from . import wordle_helper_dict


history = []
word_set = wordle_helper_dict.word_set
candidate_set = set(word_set)


def filter_with_guess_result(guess, match_result):
    def foo(word):
        for (w, g, m) in zip(word, guess, match_result):
            if m in {'.', 'X', 'x'} and g in word:
                return False

            elif m == 'O' and w != g:
                return False

            elif m == 'o':
                if w == g:
                    return False

                if g not in word:
                    return False

        return True

    return foo


def match(word, guess):
    result = ''

    buf_guess = list(guess)
    buf_word = list(word)
    for i in range(len(guess)):
        if buf_guess[i] == buf_word[i]:
            result += 'O'

        elif buf_guess[i] in buf_word:
            result += 'o'
            buf_word[buf_word.index(buf_guess[i])] = '.'

        else:
            result += '.'

    return tuple(result)


def add_guess_result(guess, result):
    global word_set
    global candidate_set

    if result == 'NNNNN':
        if guess in word_set:
            word_set.remove(guess)
        if guess in candidate_set:
            candidate_set.remove(guess)
        return

    history.append((guess, result))

    flt = filter_with_guess_result(guess, result)
    candidate_set = set(filter(flt, candidate_set))


def consult(ask):
    # if len(history) == 0:
    #     return ('guess', {'aloes', 'stoae', 'orate', 'crane'})

    if len(candidate_set) in (1, 2):
        return ('guess', candidate_set)

    if ask == 'guess':
        if len(history) == 0:
            return ('guess', {'tares'})

        def gen():
            word_set_size = len(word_set)
            best_guess = []
            best_E = 0.0
            for idx, guess in enumerate(word_set):
                E = entropy(guess)

                if E == best_E:
                    best_guess.append(guess)

                elif E > best_E:
                    best_guess = [guess]
                    best_E = E

                yield ('progress', idx, word_set_size, guess, E)

            yield ('result', set(best_guess), best_E)

        return ('guessing', gen())

    else:
        if len(history) == 0:
            return ('cost', 1)

        return ('cost', len(word_set) * (len(candidate_set) + len(list(product('Oo.', repeat=5)))))

    return ('error', {'error'})


def entropy(guess):
    candidate_num = len(candidate_set)

    E = 0.0

    match_count = {m: 0 for m in product('Oo.', repeat=5)}
    for c in candidate_set:
        match_count[match(c, guess)] += 1

    for k, v in match_count.items():
        if v == 0:
            continue

        E += v * math.log2(candidate_num / v)

    E /= candidate_num
    return E
