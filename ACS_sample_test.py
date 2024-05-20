"""Auto-completion Systems: Sample tests

"""
from ACS_prefix_tree import SimplePrefixTree, CompressedPrefixTree
from ACS_autocomplete_engines import SentenceAutocompleteEngine


def test_simple_prefix_tree_structure() -> None:
    """This is a test for the structure of a small simple prefix tree.

    NOTE: This test should pass even if you insert these values in a different
    order. This is a good thing to try out.
    """
    t = SimplePrefixTree()
    t.insert('cat', 2.0, ['c', 'a', 't'])
    t.insert('car', 3.0, ['c', 'a', 'r'])
    t.insert('dog', 4.0, ['d', 'o', 'g'])

    # t has 3 values (note that __len__ only counts the inserted values,
    # which are stored at the *leaves* of the tree).
    assert len(t) == 3

    # t has a total weight of 9.0
    assert t.weight == 2.0 + 3.0 + 4.0

    # t has two subtrees, and order matters (because of weights).
    assert len(t.subtrees) == 2
    left = t.subtrees[0]
    right = t.subtrees[1]

    assert left.root == ['c']
    assert left.weight == 5.0

    assert right.root == ['d']
    assert right.weight == 4.0


def test_simple_prefix_tree_autocomplete() -> None:
    """This is a test for the correct autocomplete behaviour for a small
    simple prefix tree.

    NOTE: This test should pass even if you insert these values in a different
    order. This is a good thing to try out.
    """
    t = SimplePrefixTree()
    t.insert('dog', 4.0, ['d', 'o', 'g'])
    t.insert('cat', 2.0, ['c', 'a', 't'])
    t.insert('car', 3.0, ['c', 'a', 'r'])

    assert t.autocomplete([]) == [('dog', 4.0), ('car', 3.0), ('cat', 2.0)]

    # But keep in mind that the greedy algorithm here does not necessarily
    # return the highest-weight values!! In this case, the ['c'] subtree
    # is recursed on first.
    assert t.autocomplete([], 1) == [('car', 3.0)]


def test_simple_prefix_tree_remove() -> None:
    """This is a test for the correct remove behaviour for a small
    simple prefix tree.

    NOTE: This test should pass even if you insert these values in a different
    order. This is a good thing to try out.
    """
    t = SimplePrefixTree()
    t.insert('cat', 2.0, ['c', 'a', 't'])
    t.insert('car', 3.0, ['c', 'a', 'r'])
    t.insert('dog', 4.0, ['d', 'o', 'g'])
    t.remove(['c', 'a'])

    assert len(t) == 1
    assert t.weight == 4.0
    assert len(t.subtrees) == 1
    assert t.subtrees[0].root == ['d']


def test_sentence_autocompleter() -> None:
    """Basic test for SentenceAutocompleteEngine.

    This test relies on the sample_sentences.csv dataset. That file consists
    of just a few lines, but there are three important details to notice:

        1. You should use the second entry of each csv file as the weight of
           the sentence. This entry can be a float! (Don't assume it's an int.)
        2. The file contains two sentences that are sanitized to the same
           string, and so this value is inserted twice. This means its weight
           is the *sum* of the weights from each of the two lines in the file.
        3. Numbers *are allowed* in the strings (this is true for both types
           of text-based autocomplete engines). Don't remove them!
    """
    engine = SentenceAutocompleteEngine({
        'file': 'data/texts/sample_sentences.csv',
        'autocompleter': 'simple'
    })

    # Check simple autocompletion and sanitization
    results = engine.autocomplete('what a')
    assert len(results) == 1
    assert results[0][0] == 'what a wonderful world'
    assert results[0][1] == 1.0

    # Check that numbers are allowed in the sentences
    results = engine.autocomplete('numbers')
    assert len(results) == 1
    assert results[0][0] == 'numbers are 0k4y'

    # Check that one sentence can be inserted twice
    results = engine.autocomplete('a')
    assert len(results) == 1
    assert results[0][0] == 'a star is born'
    assert results[0][1] == 15.0 + 6.5


if __name__ == '__main__':
    import pytest
    pytest.main(['ACS_sample_test.py'])
