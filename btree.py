from __future__ import annotations


import json
import math
from typing import List


# Node Class.
# You may make minor modifications.
class Node():
    def __init__(self,
                 keys: List[int] = None,
                 children: List[Node] = None,
                 parent: Node = None):
        self.keys = keys
        self.children = children
        self.parent = parent


# DO NOT MODIFY THIS CLASS DEFINITION.
class Btree():
    def __init__(self,
                 m: int = None,
                 root: Node = None):
        self.m = m
        self.root = None

    # DO NOT MODIFY THIS CLASS METHOD.
    def dump(self) -> str:
        def _to_dict(node) -> dict:

            return {
                "k": node.keys,
                "c": [(_to_dict(child) if child is not None else None) for child in node.children]
            }

        if self.root == None:

            dict_repr = {}
        else:

            dict_repr = _to_dict(self.root)
        return json.dumps(dict_repr, indent=2)

    # Insert.
    def insert(self, key: int):

        if self.root is None:
            self.root = Node(keys=[key], children=[None, None])

        else:
            leaf = self.find_leaf(key)
            Btree.insort_left(leaf.keys, key)
            leaf.children.append(None)

            self.split(leaf)

    def find_leaf(self, key: int):
        leaf = self.root
        if leaf is not None:
            while leaf.children[0] is not None:
                index = Btree.bisect_left(leaf.keys, key)
                leaf = leaf.children[index]
        return leaf

    def find_leftsibling(self, node):
        if not node.parent:
            return None
        idx = node.parent.children.index(node)
        if idx == 0:
            return None
        else:
            return node.parent.children[idx - 1]

    def find_rightsibling(self, node):
        if not node.parent:
            return None
        idx = node.parent.children.index(node)
        if idx == len(node.parent.children) - 1:
            return None
        else:
            return node.parent.children[idx + 1]

    def isfull(self, node):
        if node is not None:
            if len(node.keys) >= self.m - 1:
                return bool(True)
            else:
                return bool(False)
        else:
            return bool(False)

    def left_rotation(self, leaf):
        parent = leaf.parent
        leftsibling = self.find_leftsibling(leaf)
        if leftsibling and not self.isfull(leftsibling):
            parent_key_index = parent.children.index(leaf) - 1
            parent_key = parent.keys.pop(parent_key_index)
            leftsibling.keys.append(parent_key)
            leftsibling.children.append(leaf.children[0])
            if leftsibling.children[0]:
                leftsibling.children[len(leftsibling.children) - 1].parent = leftsibling
            leaf_key = leaf.keys.pop(0)
            leaf.children.remove(leaf.children[0])
            parent.keys.insert(parent_key_index, leaf_key)

        else:
            return

    def right_rotation(self, leaf):
        parent = leaf.parent
        rightsibling = self.find_rightsibling(leaf)

        if rightsibling and not self.isfull(rightsibling):

            parent_key_index = parent.children.index(leaf)
            parent_key = parent.keys.pop(parent_key_index)
            rightsibling.keys.insert(0, parent_key)
            rightsibling.children.insert(0, leaf.children[len(leaf.children) - 1])
            if rightsibling.children[0]:
                rightsibling.children[0].parent = rightsibling
            leaf_key = leaf.keys.pop()
            leaf.children.remove(leaf.children[len(leaf.children) - 1])
            parent.keys.insert(parent_key_index, leaf_key)
        else:
            return

    def split(self, leaf):

        if len(leaf.keys) > self.m - 1:

            if self.find_leftsibling(leaf) is not None and not self.isfull(self.find_leftsibling(leaf)):

                self.left_rotation(leaf)

            elif self.find_rightsibling(leaf) is not None and not self.isfull(self.find_rightsibling(leaf)):

                self.right_rotation(leaf)
            else:

                if len(leaf.keys) % 2 == 0:
                    median_idx = (len(leaf.keys) // 2) - 1
                else:
                    median_idx = len(leaf.keys) // 2

                median_key = leaf.keys[median_idx]

                new_node = Node(keys=leaf.keys[median_idx + 1:])

                new_node.children = leaf.children[median_idx + 1:]

                leaf.keys = leaf.keys[: median_idx]

                leaf.children = leaf.children[:median_idx + 1]

                if new_node.children[0]:

                    for child in new_node.children:
                        child.parent = new_node

                if leaf == self.root:

                    self.root = Node([median_key])

                    self.root.children = [leaf, new_node]

                    leaf.parent = new_node.parent = self.root

                else:
                    new_node.parent = leaf.parent
                    index = Btree.bisect_left(leaf.parent.keys, median_key)
                    leaf.parent.keys.insert(index, median_key)
                    leaf.parent.children.insert(index + 1, new_node)
                    self.split(leaf.parent)

    # Delete.
    def delete(self, key: int):

        if self.root is not None:
            if self.root.children[0] is None and key in self.root.keys:
                index = self.root.keys.index(key)

                if len(self.root.keys) == 1:

                    self.root = None
                else:
                    self.root.keys.pop(index)

                    self.root.children.pop(0)

            else:
                leaf = self.root

                if key not in leaf.keys:

                    while leaf.children[0] is not None:
                        index = Btree.bisect_left(leaf.keys, key)
                        leaf = leaf.children[index]

                        if key in leaf.keys:
                            break

                key_index = leaf.keys.index(key)

                replacement = leaf

                if replacement.children[0]:

                    replacement = replacement.children[key_index + 1]

                    replace_key = replacement.keys[0]

                    while replacement.children[0]:
                        replacement = replacement.children[0]

                    leaf.keys[key_index] = replacement.keys[0]

                    replacement.keys.pop(0)

                    replacement.children.pop(0)

                else:
                    replacement.keys.pop(key_index)
                    replacement.children.pop(0)

                self.balance(replacement)

    # Search
    def search(self, key) -> str:
        l = []
        leaf = self.root
        if self.root is not None and key not in self.root.keys:
            while leaf.children[0] is not None:
                index = Btree.bisect_left(leaf.keys, key)
                l.append(index)
                leaf = leaf.children[index]
                if key in leaf.keys:
                    break
        return json.dumps(l)

    def merge_left(self, leaf):

        parent = leaf.parent

        leftsibling = self.find_leftsibling(leaf)

        leaf_index = parent.children.index(leaf)
        parent_index = leaf_index - 1
        parent_key = parent.keys.pop(parent_index)

        leftsibling.keys.append(parent_key)
        for key in leaf.keys:
            leftsibling.keys.append(key)
        if leftsibling.children[0] and leaf.children[0]:

            for child in leaf.children:
                leftsibling.children.append(child)
                child.parent = leftsibling
        else:
            leftsibling.children.append(None)
            for key in leaf.keys:
                leftsibling.children.append(None)

        parent.children.pop(leaf_index)

    def merge_right(self, leaf):

        parent = leaf.parent

        rightsibling = self.find_rightsibling(leaf)

        rightsibling_index = parent.children.index(rightsibling)

        leaf_index = parent.children.index(leaf)

        parent_index = leaf_index
        parent_key = parent.keys.pop(parent_index)

        leaf.keys.append(parent_key)

        for key in rightsibling.keys:
            leaf.keys.append(key)

        if leaf.children[0] and rightsibling.children[0]:
            for child in rightsibling.children:
                leaf.children.append(child)
                child.parent = leaf

        else:
            leaf.children.append(None)
            for key in rightsibling.keys:
                leaf.children.append(None)

        parent.children.pop(rightsibling_index)

    def balance(self, leaf):

        smallest_key_len = math.ceil(self.m / 2) - 1

        if len(leaf.keys) < smallest_key_len:

            parent = leaf.parent

            rightsibling = self.find_rightsibling(leaf)

            leftsibling = self.find_leftsibling(leaf)
            if leftsibling is not None and len(leftsibling.keys) > smallest_key_len:
                self.right_rotation(leftsibling)

            elif rightsibling is not None and len(rightsibling.keys) > smallest_key_len:

                self.left_rotation(rightsibling)
            elif leftsibling is not None and len(leftsibling.keys) <= smallest_key_len:

                self.merge_left(leaf)
                self.balance(leftsibling.parent)

            elif rightsibling is not None and len(rightsibling.keys) <= smallest_key_len:
                self.merge_right(leaf)

                self.balance(leaf.parent)
            else:
                if self.root == leaf and len(self.root.keys) == 0:
                    self.root = leaf.children[0]

    def find_parent(self, key: int):
        leaf = self.root
        if self.root is not None and key not in self.root.keys:
            while leaf.children[0] is not None:
                index = Btree.bisect_left(leaf.keys, key)
                leaf = leaf.children[index]
                if key in leaf.keys:
                    break

        if leaf.parent:
            print(leaf.parent.keys)

    def find_children(self, key: int):
        leaf = self.root
        if self.root is not None and key not in self.root.keys:
            while leaf.children[0] is not None:
                index = Btree.bisect_left(leaf.keys, key)
                leaf = leaf.children[index]
                if key in leaf.keys:
                    break

        if leaf.children[0]:
            for child in leaf.children:
                print(child.keys)

    def bisect_left(ls:list, key:int):
        if ls is not None:
            for i in range(len(ls)):
                if ls[i] > key:
                    return i
        return len(ls)

    def insort_left(ls:list, key:int):
        index = Btree.bisect_left(ls, key)
        ls.insert(index, key)
