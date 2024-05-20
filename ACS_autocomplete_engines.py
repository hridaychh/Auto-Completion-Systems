"""Auto-completion Systems: Autocomplete engines

"""
from __future__ import annotations
import csv
import time
from typing import Any
from python_ta.contracts import check_contracts

from ACS_melody import Melody
from ACS_prefix_tree import Autocompleter, SimplePrefixTree, CompressedPrefixTree


################################################################################
# Text-based Autocomplete Engines
################################################################################
@check_contracts
class LetterAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few letters.

    The *prefix sequence* for a string is the list of characters in the string.
    This can include space characters.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters

    Instance Attributes:
    - autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
        - 'file': the path to a text file
        - 'autocompleter': either the string 'simple' or 'compressed',
          specifying which subclass of Autocompleter to use.

        Each line of the specified file counts as one input string.
        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one non-space character, it is inserted into the
        Autocompleter.

        SKIP sanitized strings that do not contain at least one non-space character!

        When each string is inserted, it is given a weight of 1.0. It is possible
        for the same string to appear on more than one line of the input file;
        this results in that string receiving a larger weight (because of how
        Autocompleter.insert works).

        Preconditions:
        - config['file'] is a valid path to a file as described above
        - config['autocompleter'] in ['simple', 'compressed']
        """
        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree()
        else:
            self.autocompleter = CompressedPrefixTree()
        words = []
        with open(config['file'], encoding='utf8') as f:
            for line in f:
                new_word = ''
                for char in line:
                    if (char.isalnum()) or (char == ' '):
                        new_word += char
                words.append(new_word.lower())

        for word in words:
            value = word
            weight = 1.0
            prefix = []
            for char in word:
                prefix.append(char)
            self.autocompleter.insert(value, weight, prefix)

    def autocomplete(self, prefix: str, limit: int | None = None) -> list[tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        sorted by non-increasing weight.

        If limit is None, return *every* match for the given prefix.

        Preconditions:
        - limit is None or limit > 0
        - <prefix> is a sanitized string
        """
        prefix_2 = []
        for char in prefix:
            prefix_2.append(char)
        return self.autocompleter.autocomplete(prefix_2, limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix string.

        Preconditions:
        - <prefix> is a sanitized string
        """
        prefix_2 = []
        for char in prefix:
            prefix_2.append(char)
        self.autocompleter.remove(prefix_2)


@check_contracts
class SentenceAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few words.

    A *word* is a string containing only alphanumeric characters.
    The *prefix sequence* for a string is the list of words in the string
    (separated by whitespace). The words themselves do not contain spaces.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters.

    Instance Attributes:
    - autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
        - 'file': the path to a CSV file
        - 'autocompleter': either the string 'simple' or 'compressed',
          specifying which subclass of Autocompleter to use.

        Preconditions:
        - config['file'] is the path to a *CSV file* where each line has two entries:
            - the first entry is a string, which is the value to store in the Autocompleter
            - the second entry is a positive float representing the weight of that
              string
        - config['autocompleter'] in ['simple', 'compressed']

        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one word, it is inserted into the Autocompleter.

        SKIP sanitized strings that do not contain at least one non-space character!

        Note that it is possible for the same string to appear on more than
        one line of the input file; this results in that string receiving
        the sum of the specified weights from each line.
        """
        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree()
        else:
            self.autocompleter = CompressedPrefixTree()
        sentences = []
        weights = []
        with open(config['file']) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                new_sentence = ''
                for char in line[0]:
                    if (char.isalnum()) or (char == ' '):
                        new_sentence += char
                sentences.append(new_sentence.lower())
                weights.append(float(line[1]))
        for i in range(len(sentences)):
            value = sentences[i]
            weight = weights[i]
            prefix = sentences[i].split(' ')
            n = prefix.count('')
            for _ in range(n):
                prefix.remove('')
            self.autocompleter.insert(value, weight, prefix)

    def autocomplete(self, prefix: str, limit: int | None = None) -> list[tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        sorted by non-increasing weight.

        If limit is None, return *every* match for the given prefix.

        Preconditions:
        - limit is None or limit > 0
        - <prefix> is a sanitized string
        """
        prefix_2 = prefix.split(' ')
        n = prefix_2.count('')
        for _ in range(n):
            prefix_2.remove('')
        return self.autocompleter.autocomplete(prefix_2, limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix.

        Preconditions:
        - <prefix> is a sanitized string
        """
        prefix_2 = prefix.split(' ')
        n = prefix_2.count('')
        for _ in range(n):
            prefix_2.remove('')
        self.autocompleter.remove(prefix_2)

################################################################################
# Melody-based Autocomplete Engines
################################################################################


@check_contracts
class MelodyAutocompleteEngine:
    """An autocomplete engine that suggests melodies based on a few intervals.

    The values stored are Melody objects, and the corresponding
    prefix sequence for a Melody is its interval sequence.

    Because the prefix is based only on interval sequence and not the
    starting pitch or duration of the notes, it is possible for different
    melodies to have the same prefix.

    Instance Attributes:
    - autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
        - 'file': the path to a CSV file
        - 'autocompleter': either the string 'simple' or 'compressed',
          specifying which subclass of Autocompleter to use.

        Preconditions:
        - config['file'] is the path to a *CSV file* where each line has the following format:
            - The first entry is the name of a melody (a string).
            - The remaining entries are grouped into pairs of integers
              where the first number in each pair is a note pitch,
              and the second number is the corresponding duration.
        - config['autocompleter'] in ['simple', 'compressed']

        HOWEVER, there may be blank entries (stored as an empty string '').
        As soon as you encounter a blank entry, stop processing this line
        and move onto the next line the CSV file.

        Each melody is inserted into the Autocompleter with a weight of 1.0.
        """
        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree()
        else:
            self.autocompleter = CompressedPrefixTree()
        melodies = []
        with open(config['file']) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                name = line[0]
                if '' in line:
                    index = line.index('')
                    line = line[1: index]
                else:
                    line = line[1:]
                notes = []
                for i in range(len(line)):
                    if i % 2 == 0:
                        notes.append((int(line[i]), int(line[i + 1])))
                melodies.append(Melody(name, notes))
        for melody in melodies:
            value = melody
            interval = []
            for i in range(len(melody.notes) - 1):
                interval.append(melody.notes[i + 1][0] - melody.notes[i][0])
            self.autocompleter.insert(value, 1.0, interval)

    def autocomplete(
        self, prefix: list[int], limit: int | None = None
    ) -> list[tuple[Melody, float]]:
        """Return up to <limit> matches for the given interval sequence.

        The return value is a list of tuples (melody, weight), and must be
        sorted by non-increasing weight.

        If limit is None, return *every* match for the given interval sequence.

        Preconditions:
        - limit is None or limit > 0
        """
        return self.autocompleter.autocomplete(prefix, limit)

    def remove(self, prefix: list[int]) -> None:
        """Remove all melodies that match the given interval sequence."""
        self.autocompleter.remove(prefix)

###############################################################################
# Sample runs
###############################################################################


def example_letter_autocomplete() -> list[tuple[str, float]]:
    """A sample run of the letter autocomplete engine.
    """
    engine = LetterAutocompleteEngine(
        {
            'file': 'data/texts/sample_words.txt',
            'autocompleter': 'simple',
        }
    )
    return engine.autocomplete('', 2)


def example_sentence_autocomplete() -> list[tuple[str, float]]:
    """A sample run of the sentence autocomplete engine.
    """
    engine = SentenceAutocompleteEngine(
        {
            'file': 'data/texts/sample_sentences.csv',
            'autocompleter': 'simple',
        }
    )
    return engine.autocomplete('a star')


def example_melody_autocomplete(play: bool = False) -> list[tuple[Melody, float]]:
    """A sample run of the melody autocomplete engine.

    If <play> is True, also play each melody using Pygame.

    """
    engine = MelodyAutocompleteEngine(
        {
            'file': 'data/melodies/more_melodies.csv',
            'autocompleter': 'simple'
        }
    )
    melodies = engine.autocomplete([5, 0], 3)

    if play:
        for melody, _ in melodies:
            melody.play()
            time.sleep(2)  # Wait 2 seconds after playing each melody
    return melodies


if __name__ == '__main__':
    # This is used to increase the recursion limit so that your autocomplete engines work
    # even for tall SimplePrefixTrees.
    import sys
    sys.setrecursionlimit(5000)

    print(example_letter_autocomplete())
    print(example_sentence_autocomplete())
    print(example_melody_autocomplete(play=True)) # May take a few sconds
