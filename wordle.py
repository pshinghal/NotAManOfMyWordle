#!/usr/bin/env python3

from collections import defaultdict


def build_lexicon():
    with open("all_words.txt", "r") as f:
        words = [line.strip() for line in f.readlines()]
    return words


def build_target_lexicon():
    with open("target_words.txt", "r") as f:
        words = [line.strip() for line in f.readlines()]
    return words


def build_freq(words, unique=True):
    freq = defaultdict(int)
    for word in words:
        for letter in set(word) if unique else word:
            freq[letter] += 1
    return freq


def valid_words(
    words, absent_letters, present_letters, disallowed_positions, known_positions
):
    return [
        word
        for word in words
        if all(letter not in word for letter in absent_letters)
        and all(letter in word for letter in present_letters)
        and all(word[idx] != letter for (letter, idx) in disallowed_positions)
        and all(word[idx] == letter for (letter, idx) in known_positions)
    ]


# TODO assign specific weight to present letter without known position being placed in a position where it isn't know to be disallowed
def letter_score(letter, freq, present_letters, absent_letters):
    if letter not in present_letters and letter not in absent_letters:
        return freq[letter]
    else:
        return 0  # penalising this encourages more exploration


# TODO instead of just looking at frequencies, also score positions separately
def score(word, freq, present_letters, absent_letters):
    return sum(
        letter_score(letter, freq, present_letters, absent_letters)
        for letter in set(word)
    )


def get_scored(words, freq, present_letters, absent_letters):
    return sorted(
        [(word, score(word, freq, present_letters, absent_letters)) for word in words],
        key=(lambda x: -x[1]),
    )


def guess(words, freq, present_letters, absent_letters):
    return get_scored(words, freq, present_letters, absent_letters)[:10]


# result takes form 'GYBBY' (green, yellow, black)
def get_constraints(guess, result):
    absent_letters = set()
    present_letters = set()
    disallowed_positions = set()
    known_positions = set()
    for (idx, letter, color) in zip(range(5), guess, result):
        if color == "G":
            present_letters.add(letter)
            known_positions.add((letter, idx))
        elif color == "Y":
            present_letters.add(letter)
            disallowed_positions.add((letter, idx))
        elif color == "B":
            absent_letters.add(letter)
    return (absent_letters, present_letters, disallowed_positions, known_positions)


def merge_constraints(old_al, old_pl, old_dp, old_kp, new_al, new_pl, new_dp, new_kp):
    return (
        old_al.union(new_al),
        old_pl.union(new_pl),
        old_dp.union(new_dp),
        old_kp.union(new_kp),
    )


def run_loop():
    absent_letters = set()
    present_letters = set()
    disallowed_positions = set()
    known_positions = set()
    lexicon = build_lexicon()
    valid = build_target_lexicon()
    while len(valid) > 1:
        freq = build_freq(valid)
        if len(valid) < 10:
            print(f"Fewer than 10 valid choices remain: {valid}")
        print(
            f"Suggestions for next word: {guess(lexicon, freq, present_letters, absent_letters)}"
        )
        guessed = input("What word did you guess? ")
        result = input("What was the result (formatted like YBBGB)? ")
        al, pl, dp, kp = get_constraints(guessed, result)
        (
            absent_letters,
            present_letters,
            disallowed_positions,
            known_positions,
        ) = merge_constraints(
            absent_letters,
            present_letters,
            disallowed_positions,
            known_positions,
            al,
            pl,
            dp,
            kp,
        )
        valid = valid_words(
            valid,
            absent_letters,
            present_letters,
            disallowed_positions,
            known_positions,
        )
    print(f"The word is {valid[0]}")


if __name__ == "__main__":
    run_loop()
