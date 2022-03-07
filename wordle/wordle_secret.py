import datetime
import random

from . import wordle_official_dict


class WordleSecret:
    def __init__(self, key=None):
        self.answer_set = wordle_official_dict.answer_set
        self.allow_set = wordle_official_dict.allow_set
        self.words_loaded = len(self.answer_set) + len(self.allow_set)

        wordle_first_date = datetime.date(2021, 6, 19)

        self.index = None
        self.secret = None
        self.date = None

        today_date = datetime.date.today()
        today_index = (today_date - wordle_first_date).days

        if key is None:
            wordle_index_limit = (today_date - wordle_first_date).days - 1
            self.index = random.randrange(wordle_index_limit)

        elif isinstance(key, str):
            if key not in self.answer_set:
                raise Exception('Invalid word: ' + key)

            self.index = self.answer_set.index(key)

        elif isinstance(key, int):
            if key >= len(self.answer_set):
                raise Exception('Invalid index: ' + key)

            if key > today_index:
                raise Exception('No future quiz')

            self.index = key

        elif isinstance(key, datetime.date):
            if key > today_date:
                raise Exception('No future quiz')

            self.index = (key - wordle_first_date).days

        else:
            raise Exception('Unrecognized key: ' + repr(key))

        self.secret = self.answer_set[self.index]
        self.date = wordle_first_date + datetime.timedelta(days=self.index)

    @property
    def title(self):
        return 'Wordle #{idx} ({yyyy:0>4}/{mm:0>2}/{dd:0>2})'.format(
            idx=self.index, yyyy=self.date.year, mm=self.date.month, dd=self.date.day)

    def match(self, guess):
        if guess not in self.answer_set and guess not in self.allow_set:
            return 'NNNNN'

        ret = ''
        for (s, g) in zip(self.secret, guess):
            if s == g:
                ret += 'O'
            elif g in self.secret:
                ret += 'o'
            else:
                ret += 'X'

        return ret

    def __str__(self):
        return self.secret
