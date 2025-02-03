class SimpleSuffixTreeNode:
    def __init__(self, key):
        self.key = key
        self.children = {}
        self.positions = []

    def getChild(self, key):
        return self.children.get(key)


class SimpleSuffixTree:
    def __init__(self):
        self.root = SimpleSuffixTreeNode('Root')

    def insertWord(self, parent, word, position):
        if len(word) == 0:
            if '$' not in parent.children:
                parent.children['$'] = SimpleSuffixTreeNode('$')
            parent.children['$'].positions.append(position)
            return
        childNode = parent.getChild(word[0])
        # Add Child Node if none exists
        if childNode is None:
            parent.children[word[0]] = SimpleSuffixTreeNode(word[0])

        parent.children[word[0]].positions.append(position)

        self.insertWord(parent.children[word[0]], word[1:], position)

    def searchWord(self, parent, word):
        if len(word) == 0:
            return parent.positions

        childNode = parent.getChild(word[0])

        if childNode is None:
            return []

        return self.searchWord(parent.children[word[0]], word[1:])

    def print_tree(self, node=None, depth=0):
        if node is None:
            node = self.root
        for char, child in node.children.items():
            print("  " * depth + f"({char}) -> Index: {child.positions}")
            self.print_tree(child, depth + 1)


class CompactSuffixTreeNode:
    def __init__(self, leaf=False):
        self.children = {}  # Dictionary of child nodes
        self.leaf = leaf  # Is this a leaf node?
        self.suffix_link = None  # Suffix link to another node
        self.start = None  # Start index of substring
        self.end = None  # End index of substring
        self.suffix_index = None  # Index of suffix for leaf nodes


class CompactSuffixTree:
    def __init__(self, text):
        self.text = text + "$"  # Append terminal character
        self.root = CompactSuffixTreeNode()
        self.active_node = self.root
        self.active_edge = -1
        self.active_length = 0
        self.remainder = 0
        self.current_node = None
        self.pos = -1
        self.tree_end = -1

        # Build the tree
        self._build()

    def _edge_length(self, node):
        if node.end is None:
            return self.tree_end - node.start + 1
        return node.end - node.start + 1

    def _walk_down(self, current_node):
        if self.active_length >= self._edge_length(current_node):
            self.active_edge += self._edge_length(current_node)
            self.active_length -= self._edge_length(current_node)
            self.active_node = current_node
            return True
        return False

    def _new_node(self, start, end=None, leaf=False):
        node = CompactSuffixTreeNode(leaf)
        node.start = start
        node.end = end
        return node

    def _extend_tree(self, pos):
        self.tree_end = pos
        self.remainder += 1
        self.current_node = None

        while self.remainder > 0:
            if self.active_length == 0:
                self.active_edge = pos

            if self.text[self.active_edge] not in self.active_node.children:
                leaf = self._new_node(pos, None, True)
                leaf.suffix_index = pos - self.remainder + 1
                self.active_node.children[self.text[self.active_edge]] = leaf

                if self.current_node is not None:
                    self.current_node.suffix_link = self.active_node
                    self.current_node = None

            else:
                next_node = self.active_node.children[self.text[self.active_edge]]

                if self._walk_down(next_node):
                    continue

                if self.text[next_node.start + self.active_length] == self.text[pos]:
                    if self.current_node is not None:
                        self.current_node.suffix_link = self.active_node
                    self.active_length += 1
                    break

                split = self._new_node(next_node.start, next_node.start + self.active_length - 1)
                self.active_node.children[self.text[self.active_edge]] = split

                leaf = self._new_node(pos, None, True)
                leaf.suffix_index = pos - self.remainder + 1
                split.children[self.text[pos]] = leaf

                next_node.start += self.active_length
                split.children[self.text[next_node.start]] = next_node

                if self.current_node is not None:
                    self.current_node.suffix_link = split
                self.current_node = split

            self.remainder -= 1

            if self.active_node == self.root and self.active_length > 0:
                self.active_length -= 1
                self.active_edge = pos - self.remainder + 1
            elif self.active_node != self.root:
                self.active_node = self.active_node.suffix_link if self.active_node.suffix_link else self.root

    def _build(self):
        for i in range(len(self.text)):
            self._extend_tree(i)

    def search_pattern(self, pattern):
        if not pattern or len(pattern) > len(self.text) - 1:  # -1 for the terminal $
            return []

        def check_edge(node, start_pos, pattern_pos):
            edge_pos = 0
            edge_end = node.end if node.end is not None else self.tree_end

            while pattern_pos < len(pattern) and edge_pos <= edge_end - node.start:
                if pattern_pos >= len(pattern):
                    return True, pattern_pos
                if edge_pos > edge_end - node.start:
                    return True, pattern_pos
                if pattern[pattern_pos] != self.text[node.start + edge_pos]:
                    return False, pattern_pos
                pattern_pos += 1
                edge_pos += 1
            return True, pattern_pos

        def find_pattern_positions(node, pattern_pos, positions):
            if pattern_pos == len(pattern):
                # We found the pattern, collect all leaf positions
                stack = [(node, 0)]
                while stack:
                    current, depth = stack.pop()
                    if current.leaf:
                        #positions.append(current.suffix_index)
                        """ To Let start index use 1 not as machine use 0 to start"""
                        positions.append(current.suffix_index+1)
                    else:
                        for child in current.children.values():
                            stack.append((child, depth + 1))
                return

            # Try matching pattern along children
            for char, child in node.children.items():
                if char == pattern[pattern_pos]:
                    matches, new_pos = check_edge(child, pattern_pos, pattern_pos)
                    if matches:
                        find_pattern_positions(child, new_pos, positions)

        positions = []
        find_pattern_positions(self.root, 0, positions)
        return sorted(positions)

    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root

        for char, child in node.children.items():
            edge_end = child.end if child.end is not None else self.tree_end
            suffix_info = f" (idx:{child.suffix_index})" if child.leaf else ""
            print('  ' * level + f"'{char}' -> {self.text[child.start:edge_end + 1]}{suffix_info}")
            self.print_tree(child, level + 1)


def read_sequence_from_file(filename):
    with open(filename, 'r') as file:
        return file.read().strip()


def main():
    filename = input("Please input the file name:")
    sequence = read_sequence_from_file(filename)
    substring = input("Please input the substring:")

    type_tree = input("Please input the type of suffix tree:")
    if type_tree == "Simple Suffix Tree":
        suffix_tree = SimpleSuffixTree()
        for i in range(len(sequence)):
            suffix_tree.insertWord(suffix_tree.root, sequence[i:], i + 1)

        positions = suffix_tree.searchWord(suffix_tree.root, substring)
        if not positions:
            print("Not Found")  # Substring not found
        else:
            print(" ".join(map(str, positions)))  # Print positions separated by spaces

    elif type_tree == "Compact Suffix Tree":
        suffix_tree = CompactSuffixTree(sequence)

        positions = suffix_tree.search_pattern(substring)
        if not positions:
            print("Not Found")  # Substring not found
        else:
            print(" ".join(map(str, positions)))  # Print positions separated by spaces
    else:
        print("Wrong type of suffix tree")


if __name__ == "__main__":
    """ if use Simple Suffix Tree, when the string is really long, 
    will case the recursion limit error,
    so modify the recursionlimit when is needed
     """
    import sys
    sys.setrecursionlimit(10000)
    main()
