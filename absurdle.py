#!/usr/bin/env python3

from wordle import build_lexicon, build_target_lexicon, build_freq
from itertools import combinations

lex = build_lexicon()
targets = build_target_lexicon()

excluded_indices = {}

for word in lex:
    excluded_letters = set(word)
    excluded_indices[word] = set(
        idx
        for idx, target in enumerate(targets)
        # if making a set is cheaper, maybe try set(target) instead?
        if any(letter in excluded_letters for letter in target)
    )

most_excluding_words = sorted(
    ((word, len(ei)) for word, ei in excluded_indices.items()), key=lambda x: -x[1]
)
freq = build_freq(targets, unique=True)


def get_kicker_score(word, freq):
    return max(freq[letter] for letter in word)


i = 0
max_excluders = ("NOPE", "NOPE")
# "kicker" is the adversary's "escape"
# i.e. the highest-scoring letter in the second word
# We want to minimize this to give the adversary the smallest escape
max_kicker_score = 0
max_excluded = 0
promising_words = [word for word in lex if len(word) == len(set(word))]


def analyse(max_max_excluded=0, naive_kicker=True):
    i = 0
    max_excluders = ("NOPE", "NOPE")
    # "kicker" is the adversary's "escape"
    # i.e. the highest-scoring letter in the second word
    # We want to minimize this to give the adversary the smallest escape
    max_kicker_score = 0
    max_excluded = 0
    for first, second in combinations(promising_words, 2):
        if i % 100000 == 0:
            print(f"Processed {i}")
            print(
                f"Max excluders are {max_excluders} with {max_excluded} exclusions and kicker score {max_kicker_score}"
            )
        i += 1
        if len(first + second) != len(set(first + second)):
            continue
        num_excluded = len(excluded_indices[first].union(excluded_indices[second]))
        # skip everything that ends with no options (in which case the adversary would
        # obviously not take this route)
        if num_excluded == len(targets):
            continue
        if max_max_excluded != 0 and num_excluded > max_max_excluded:
            continue
        if num_excluded >= max_excluded:
            kicker_score = 0
            if naive_kicker:
                # naively, the kicker score can be based on the letter that has the
                # largest word count in the original targets
                kicker_score = get_kicker_score(second, freq)
            else:
                # non-naively, the kicker score should the actual number of remaining
                # possible words
                for kicker in set(second):
                    second_absent_letters = set(second)
                    second_absent_letters.remove(kicker)
                    kicker_score = max(
                        kicker_score,
                        sum(
                            1
                            for (idx, word) in enumerate(targets)
                            if idx not in excluded_indices[first]
                            and kicker in word
                            and not any(
                                letter in second_absent_letters for letter in word
                            )
                        ),
                    )
            if num_excluded > max_excluded or kicker_score <= max_kicker_score:
                max_excluded = num_excluded
                max_excluders = (first, second)
                max_kicker_score = kicker_score


analyse(2300, False)
