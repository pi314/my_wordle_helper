import readline

import datetime
import random
import re
import sys

from . import wordle_helper
from .wordle_secret import WordleSecret


class WordleUIGlobalVars:
    def __init__(self):
        self.title = 'WordleUI'
        self.info = ''
        self.keycap_hit = {c: '?' for c in 'qwertyuiopasdfghjklzxcvbnm'.upper()}
        self.keyboard_layout = 'qwerty'
        self.history = []
        self.game_end = False
        self.secret = None
        self.ask_one = False
        self.auto = False
        self.helper_guess = None

wordle_ui = WordleUIGlobalVars()


def render_keyboard():

    if wordle_ui.keyboard_layout.upper() == 'DVORAK':
        keyboard_template = '\n'.join([
            '╔══════════╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤══╗',
            '║  Wordle  │{P}│{Y}│{F}│{G}│{C}│{R}│{L}│  ║',
            '╟───┬───┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬─╢',
            '║{A}│{O}│{E}│{U}│{I}│{D}│{H}│{T}│{N}│{S}│ ║',
            '╟─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─╢',
            '║ │ ; │{Q}│{J}│{K}│{X}│{B}│{M}│{W}│{B}│{Z}║',
            '╚═╧═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝',
        ])

    else:
        keyboard_template = '\n'.join([
            '╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗',
            '║{Q}│{W}│{E}│{R}│{T}│{Y}│{U}│{I}│{O}│{P}║',
            '╟┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──╢',
            '║│{A}│{S}│{D}│{F}│{G}│{H}│{J}│{K}│{L}│  ║',
            '║└─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴───┴──╢',
            '║  │{Z}│{X}│{C}│{V}│{B}│{N}│{M}│ Wordle ║',
            '╚══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╧════════╝',
        ])

    print(keyboard_template.format(**{key: render_keycap(key, hit) for key, hit in wordle_ui.keycap_hit.items()}))


def render_keycap(key, hit):
    return {
            'O': lambda x: '\033[0;30;42m ' + x.upper() + ' \033[m',
            'o': lambda x: '\033[0;30;43m ' + x.upper() + ' \033[m',
            'X': lambda x: '\033[0;37;40m ' + x.upper() + ' \033[m',
            'N': lambda x: '\033[0;30;41m ' + x.upper() + ' \033[m',
            '?': lambda x: '\033[0;30;47m ' + x.upper() + ' \033[m',
    }.get(hit, lambda x: '(' + x.lower() + ')')(key)


def render_ui():
    print('=' * 79)
    print('\033[H\033[J', end='')   # clear screen

    print(wordle_ui.title)
    print()
    print('Guesses:')

    print('┌─────────────────┐')
    for h in wordle_ui.history:
        pretty_print_guess_result(h[0], h[1])

    for i in range(6 - len(wordle_ui.history)):
        print('│  .  .  .  .  .  │')

    print('└─────────────────┘')

    render_keyboard()
    print()

    helper_access_type, helper_assess_result = wordle_helper.consult('guess' if wordle_ui.ask_one else 'cost')
    wordle_ui.ask_one = False

    if len(wordle_helper.candidate_set) < 10:
        print('helper: {} candidates: {}'.format(len(wordle_helper.candidate_set), wordle_helper.candidate_set))
    else:
        print('helper: {} candidates'.format(len(wordle_helper.candidate_set)))

    if helper_access_type == 'guess':
        wordle_ui.helper_guess = random.choice(list(helper_assess_result))
        print('helper: guess={}'.format(wordle_ui.helper_guess))

    elif helper_access_type == 'guessing':
        helper_guess = None
        helper_E = 0
        for tag, *value in helper_assess_result:
            if tag == 'progress':
                (idx, total, guess, E) = value
                print('\rhelper: [{}/{}]: checking={}, E={}'.format(idx, total, guess, E), end='')

            elif tag == 'result':
                (helper_guess, helper_E) = value
                print('\rhelper: guess={}, E={}'.format(helper_guess, helper_E), end='')

        print('\r' + (' ' * 80), end='')
        print('\rhelper: guess={}, E={}'.format(helper_guess, helper_E), end='')

        wordle_ui.helper_guess = random.choice(list(helper_guess))

    else:
        print('helper:', helper_access_type, helper_assess_result)

    print()

    print('[info]', wordle_ui.info)
    print()


def pretty_print_guess_result(guess, result):
    buf = ''
    for g, r in zip(guess, result):
        buf += render_keycap(g, r)

    print('│ ' + buf + ' │')


def add_guess_result(guess, result):
    if not wordle_ui.history or wordle_ui.history[-1][1] != 'NNNNN':
        wordle_ui.history.append((guess, result))
    else:
        wordle_ui.history[-1] = (guess, result)

    if result != 'NNNNN':
        wordle_helper.add_guess_result(guess, result)

    score = dict(zip(['?', 'N', 'X', 'o', 'O'], [0, 0, 1, 2, 3]))

    for G, r in zip(guess.upper(), result):
        if score[r] > score[wordle_ui.keycap_hit[G]]:
            wordle_ui.keycap_hit[G] = r

    if len(wordle_ui.history) >= 6:
        wordle_ui.game_end = True

    if result == 'OOOOO':
        wordle_ui.game_end = True


def loop():
    while not wordle_ui.game_end:
        render_ui()

        if wordle_ui.auto:
            guess = wordle_ui.helper_guess
            wordle_ui.ask_one = True
        else:
            guess = input('Guess> ').strip()

        wordle_ui.info = guess

        if not guess:
            wordle_ui.ask_one = True

        elif guess in (':auto', 'gogo', ':gogo'):
            wordle_ui.auto = True

        elif guess in ('exit', ':exit'):
            game_end = True

        elif guess in (':dvorak', ':qwerty'):
            wordle_ui.keyboard_layout = guess.lstrip(':')

        elif len(guess) == 5:
            wordle_ui.info = 'Guess: ' + guess
            result = wordle_ui.secret.match(guess)
            add_guess_result(guess, result)

            if result == 'NNNNN':
                wordle_ui.info = 'Invalid guess: ' + guess

        else:
            wordle_ui.info = 'Invalid guess: ' + guess

    wordle_ui.info = 'Answer: ' + str(wordle_ui.secret)
    render_ui()


def main():
    if len(sys.argv) == 2:
        key = sys.argv[1].lower()

        if re.match(r'^\d+$', key):
            wordle_ui.secret = WordleSecret(int(key))

        elif re.match(r'^\d\d\d\d/\d\d/\d\d$', key):
            wordle_ui.secret = WordleSecret(datetime.date(*map(int, key.split('/'))))

        elif key == '.':
            wordle_ui.secret = WordleSecret(datetime.date.today())

        else:
            wordle_ui.secret = WordleSecret(key)

    else:
        wordle_ui.secret = WordleSecret()

    wordle_ui.title = wordle_ui.secret.title
    wordle_ui.info = str(wordle_ui.secret.words_loaded) + ' words loaded'

    loop()
