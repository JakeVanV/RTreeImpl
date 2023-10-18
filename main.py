import colorsys

import random
from time import sleep
from typing import List
import draw_tree
import math_utils

# PARAMETERS

M = 4
m = M // 2

label_count = 0


class TreeEntry:
    def __init__(self, rect):
        self.rect = rect

        global label_count
        label_count += 1
        self.label = label_count

        self.color = generate_random_color()


random.seed(8)


def generate_random_color():
    return colorsys.hsv_to_rgb(random.random(), 1, 1)


class Node:
    def __init__(self, parent):
        # Non-leaf nodes only
        self.children: List[Node] = []
        self.mbr = [-1, -1, -1, -1]

        # Leaf Nodes only
        self.entries: List[TreeEntry] = []

        # Both
        global label_count
        label_count += 1
        self.label = "M" + str(label_count)
        self.parent = parent

    def is_leaf(self) -> bool:
        return len(self.entries) != 0

    def is_root(self):
        return self == root_node

    def calculate_mbrs(self):
        # Calculate MBRs of children first
        if not self.is_leaf():
            for child in self.children:
                child.calculate_mbrs()

        x1, y1, x2, y2 = (10000000, 1000000, -1, -1)
        e = self.entries if self.is_leaf() else self.children
        for ent in e:
            rect = ent.rect if self.is_leaf() else ent.mbr
            x1 = min(x1, rect[0])
            y1 = min(y1, rect[1])

            x2 = max(x2, rect[2])
            y2 = max(y2, rect[3])
        self.mbr = [x1, y1, x2, y2]

    def get_needed_enlargement(self, b):
        a = self.mbr
        xd = abs(b[2] - a[2])
        yd = abs(b[3] - a[3])
        return xd * yd


# As defined in paper
def choose_leaf(insert_child):
    node = root_node
    while True:
        min_enlargement = 100000000000
        min_child = None
        for child in node.children:
            needed_enlargement = child.get_needed_enlargement(insert_child.mbr)
            if needed_enlargement < min_enlargement:
                min_enlargement = needed_enlargement
                min_child = child
        if node.is_leaf():
            return node
        else:
            node = min_child

def split_node(node):
    all_combos = get_all_split_possibilities(node.children)
    best_combo = None
    min_size = 1000000000000
    for child in all_combos:
        mbr1 = math_utils.calculate_mbr(child[0])
        mbr2 = math_utils.calculate_mbr(child[1])
        total_size = math_utils.get_area(mbr1) + math_utils.get_area(mbr2)
        if total_size <= min_size:
            min_size = total_size
            best_combo = child


def get_all_split_possibilities(l):
    # Exhaustive Algorithm
    all_combinations = []
    for r in range(1, len(l)): # Excluding 0 and L length, never want that
        import itertools
        comb = []
        for combo in itertools.combinations(l, r):
            comb.append((combo, set(l) - set(combo)))
        all_combinations.extend(comb)

    return all_combinations

root_node = Node(parent=None)


def generate_tree(node, max_depth):
    if max_depth == 0:
        num_entries = random.randint(2, 4)
        for _ in range(num_entries):
            x, y = random.uniform(0, 100), random.uniform(0, 100)
            rect = [x, y, x + random.uniform(1, 44), y + random.uniform(1, 44)]
            node.entries.append(TreeEntry(rect))
    else:
        num_children = random.randint(2, 4)
        for _ in range(num_children):
            child = Node(parent=node)
            generate_tree(child, max_depth - 1)
            node.children.append(child)


generate_tree(root_node, 1)

# n1 = Node()
# n2 = Node()
#
# n1.entries.append(TreeEntry([3, 3, 4, 4]))
# n1.entries.append(TreeEntry([5, 5, 10, 10]))
#
# n2.entries.append(TreeEntry([2, 3, 4, 8]))
# n2.entries.append(TreeEntry([5, 1, 10, 7]))
#
# root_node.children.append(n1)
# root_node.children.append(n2)

root_node.calculate_mbrs()
print("f")


def get_leaf_nodes(root, nodes):
    if root.is_leaf():
        nodes.append(root)
    else:
        for child in root.children:
            get_leaf_nodes(child, nodes)


def traverse_tree_and_collect_entries(node, entry_list, node_list):
    node_list.append(node)
    if node.is_leaf():
        entry_list.extend(node.entries)
    else:
        for child in node.children:
            traverse_tree_and_collect_entries(child, entry_list, node_list)


import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.ion()


def draw_rectangles(rectangles, nodes):
    fig, ax, = plt.subplots(figsize=(12, 6))

    ax.grid(True)
    ax.set_axisbelow(True)
    # ax.yaxis.grid(color='gray', linestyle='dashed')
    # ax.xaxis.grid(color='gray', linestyle='dashed')
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 15)
    ax.locator_params(nbins=10, tight=True)

    for ent in rectangles:
        x1, y1, x2, y2 = ent.rect
        colour = ent.color
        c2 = colour + (0.3,)
        ax.add_patch(patches.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=True, linewidth=2,
                                       edgecolor=colour, facecolor=c2))
        ax.text(x1 + 0.1, y2 - 0.1, str(ent.label), color='black', fontsize=12, va='top', ha='left')

    for node in nodes:
        x1, y1, x2, y2 = node.mbr
        colour = (0, 0, 0, 0.5)
        SP = 0.05  # spacer
        ax.add_patch(patches.Rectangle((x1 - SP, y1 - SP), SP * 2 + x2 - x1, SP * 2 + y2 - y1, fill=False, linewidth=2,
                                       linestyle='-',
                                       edgecolor=colour))
        ax.text(x2 - 1, y2 - 0.1, node.label, color='black', fontsize=12, va='top', ha='left')

    plt.axis('equal')

    # lnodes = []
    # get_leaf_nodes(root_node, lnodes)
    # draw_tree.draw_tree(root_node, lnodes, axz)
    plt.show()


entries = []
nodes = []
traverse_tree_and_collect_entries(root_node, entries, nodes)
draw_rectangles(entries, nodes)

import draw_tree

draw_tree.from_root(root_node)

while True:
    plt.pause(0.1)
