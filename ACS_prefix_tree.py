"""Auto-completion Systems: Autocompleter classes
"""
from __future__ import annotations
from typing import Any
from python_ta.contracts import check_contracts


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """
    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: list) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this autocompleter
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
        - weight > 0
        - the given value is either:
            1) not in this Autocompleter, or
            2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: list,
                     limit: int | None = None) -> list[tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        sorted by non-increasing weight. You can decide how to break ties.

        If limit is None, return *every* match for the given prefix.

        Preconditions:
        - limit is None or limit > 0
        """
        raise NotImplementedError

    def remove(self, prefix: list) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree
################################################################################


@check_contracts
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    Instance Attributes:
    - root:
        The root of this prefix tree.
        - If this tree is empty, <root> equals [].
        - If this tree is a leaf, <root> represents a value stored in the Autocompleter
          (e.g., 'cat').
        - If this tree is not a leaf and non-empty, <root> is a list representing a prefix
          (e.g., ['c', 'a']).
    - subtrees:
        A list of subtrees of this prefix tree.
    - weight:
        The weight of this prefix tree.
        - If this tree is empty, this equals 0.0.
        - If this tree is a leaf, this stores the weight of the value stored in the leaf.
        - If this tree is not a leaf and non-empty, this stores the *total weight* of
          the leaf weights in this tree.

    Representation invariants:
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0.0, then self.root == [] and self.subtrees == [].
        This represents an empty prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, then this tree is a leaf.
        (self.root is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If self.subtrees != [], then self.root is a list (representing a prefix),
        and self.weight is equal to the sum of the weights of all leaves in self.

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of weight.

      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a weight
      attribute.
    """
    root: Any
    weight: float
    subtrees: list[SimplePrefixTree]

    def __init__(self) -> None:
        """Initialize an empty simple prefix tree.
        """
        self.root = []
        self.subtrees = []
        self.weight = 0.0

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return (self.subtrees == []) and (self.weight > 0.0)

    def __len__(self) -> int:
        """Return the number of LEAF values stored in this prefix tree.

        """
        if self.is_empty():
            return 0
        elif self.is_leaf():
            return 1
        else:
            length = 0
            for subtree in self.subtrees:
                length += subtree.__len__()
            return length

    ###########################################################################
    # Extra helper methods
    ###########################################################################

    def __str__(self) -> str:
        """Return a string representation of this prefix tree.

        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this prefix tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.root} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def insert(self, value: Any, weight: float, prefix: list) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this autocompleter
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
        - weight > 0
        - the given value is either:
            1) not in this Autocompleter, or
            2) was previously inserted with the SAME prefix sequence
        - prefix[0:len(self.root)] == self.root
        """
        if len(prefix) == 0:
            leaf = SimplePrefixTree()
            leaf.root = value
            leaf.subtrees = []
            if not self.subtrees:
                self.weight = weight
                leaf.weight = weight
                self.subtrees.extend([leaf])
            else:
                if value not in self.get_leaf_value():
                    leaf.weight = weight
                    self.subtrees.extend([leaf])
                    self.weight += weight
                else:
                    for subtree in self.subtrees:
                        if subtree.root == value:
                            subtree.weight += weight
                            self.weight += weight
        else:
            node = self.create_node(self.root, prefix[0: 1], weight)
            if node.root not in self.get_subtree_roots(self.subtrees):
                self.subtrees.extend([node])
                if len(self.subtrees) <= 1:
                    self.weight = weight
                else:
                    self.weight += weight
                self.subtrees[-1].insert(value, weight, prefix[1:])
            else:
                self.weight += weight
                index = self.get_subtree_roots(self.subtrees).index(node.root)
                self.subtrees[index].insert(value, weight, prefix[1:])
        self.subtrees.sort(key=lambda sub_tree: sub_tree.weight, reverse=True)

    def create_node(self, initial: Any, value: Any, weight: float) -> SimplePrefixTree:
        """Creates and returns a new node for this tree.
        """
        node = SimplePrefixTree()
        node.root = initial + value
        node.weight = weight
        node.subtrees = []
        return node

    def get_subtree_roots(self, subtrees: list[SimplePrefixTree]) -> list:
        """Returns a list of all subtree roots.
        """
        lst = []
        for subtree in subtrees:
            lst.append(subtree.root)
        return lst

    def get_leaf_value(self) -> list:
        """Returns a list of all leaf values in this tree.
        """
        if self.is_empty():
            return []
        elif self.is_leaf():
            return [self.root]
        else:
            leaves = []
            for subtree in self.subtrees:
                leaves.extend(subtree.get_leaf_value())
            return leaves

    def get_leaves(self) -> list[SimplePrefixTree]:
        """Returns a list of all leaves in this tree.
        """
        if self.is_empty():
            return []
        elif self.is_leaf():
            return [self]
        else:
            leaves = []
            for subtree in self.subtrees:
                leaves.extend(subtree.get_leaves())
            return leaves

    def autocomplete(self, prefix: list,
                     limit: int | None = None) -> list[tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        sorted by non-increasing weight.

        If limit is None, return *every* match for the given prefix.

        Preconditions:
        - limit is None or limit > 0
        """
        if limit is None:
            if self.root == prefix:
                leaves = self.get_leaves()
                lst = []
                for leaf in leaves:
                    lst.append((leaf.root, leaf.weight))
                lst.sort(key=lambda tup: tup[1], reverse=True)
                return lst
            else:
                lst = []
                for subtree in self.subtrees:
                    lst.extend(subtree.autocomplete(prefix, limit))
                return lst
        else:
            if self.root == prefix:
                leaves = self.get_leaves()
                lst = []
                for i in range(min(limit, len(leaves))):
                    lst.append((leaves[i].root, leaves[i].weight))
                return lst
            else:
                lst = []
                for subtree in self.subtrees:
                    lst.extend(subtree.autocomplete(prefix, limit))
                return lst

    def remove(self, prefix: list) -> None:
        """Remove all values that match the given prefix.
        """
        if not prefix:
            self.root = []
            self.subtrees = []
            self.weight = 0.0
        else:
            if self.root == prefix:
                self.root = []
                self.subtrees = []
                self.weight = 0.0
            else:
                for subtree in self.subtrees:
                    subtree_wt = subtree.weight
                    subtree.remove(prefix)
                    if subtree.is_empty():
                        self.weight = self.weight - subtree_wt
                        self.subtrees.remove(subtree)

################################################################################
# CompressedPrefixTree
################################################################################


@check_contracts
class CompressedPrefixTree(SimplePrefixTree):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version reduces the number of
    tree objects used to store values in the tree.

    Representation Invariants:
    - (NEW) This tree does not contain any compressible internal values.
    """
    subtrees: list[CompressedPrefixTree]  # Note the different type annotation


if __name__ == '__main__':
    import doctest
    doctest.testmod()
