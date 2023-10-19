import colorsys

import random
from time import sleep
from typing import List
import draw_tree
import math_utils
import itertools

# PARAMETERS

M = 4
MIN_ELEM = 1

label_count = 0


class TreeEntry:
    def __init__(self, rect, parent):
        self.mbr = rect
        self.parent = parent

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
        self.children = []
        self.mbr = [-1, -1, -1, -1]

        # Both
        global label_count
        label_count += 1
        self.label = "M" + str(label_count)
        self.parent = parent

        self.color = (0,0,0)

    def is_leaf(self) -> bool:
        return isinstance(self.children[0], TreeEntry)

    def is_root(self):
        return self == root_node

    def calculate_mbr_self(self):
        x1, y1, x2, y2 = (10000000, 1000000, -1, -1)
        for ent in self.children:
            rect = ent.mbr
            x1 = min(x1, rect[0])
            y1 = min(y1, rect[1])

            x2 = max(x2, rect[2])
            y2 = max(y2, rect[3])
        self.mbr = [x1, y1, x2, y2]

    def calculate_mbrs(self):
        # Calculate MBRs of children first
        if not self.is_leaf():
            for child in self.children:
                child.calculate_mbrs()

        x1, y1, x2, y2 = (10000000, 1000000, -1, -1)
        for ent in self.children:
            rect = ent.mbr
            x1 = min(x1, rect[0])
            y1 = min(y1, rect[1])

            x2 = max(x2, rect[2])
            y2 = max(y2, rect[3])
        self.mbr = [x1, y1, x2, y2]

    # based on surface area

    # based on min axis
    def get_needed_enlargement(self, rect_b):
        rect_a = self.mbr

        enlarged_rect = math_utils.calculate_mbr([rect_a, rect_b])
        enlarged_area = math_utils.get_area(enlarged_rect)
        old_area = math_utils.get_area(rect_a)

        return enlarged_area - old_area


# As defined in paper
def choose_leaf(insert_child):
    node = root_node
    while True:
        if node.is_leaf():
            return node
        min_enlargement = 100000000000
        min_child = None
        for child in node.children:
            needed_enlargement = child.get_needed_enlargement(insert_child.mbr)
            if needed_enlargement < min_enlargement:
                min_enlargement = needed_enlargement
                min_child = child

        node = min_child


def split_node(node):
    all_combos = get_all_split_possibilities(node.children)
    best_combo = None
    min_size = 1000000000000
    for child in all_combos:
        mbr1 = math_utils.calculate_mbr([yx.mbr for yx in child[0]])
        mbr2 = math_utils.calculate_mbr([yx.mbr for yx in child[1]])
        total_size = math_utils.get_area(mbr1) + math_utils.get_area(mbr2)
        if total_size <= min_size:
            min_size = total_size
            best_combo = child

    node.children.clear()
    # Create new node
    node_b = Node(parent=node.parent)
    node_b.parent.children.append(node_b)

    node.children.extend(best_combo[0])
    node_b.children.extend(best_combo[1])

    # TODO no re-calculating the entire MBR tree
    node.calculate_mbr_self()
    node_b.calculate_mbr_self()
    node.parent.calculate_mbr_self()
    # root_node.calculate_mbrs()


def adjust_tree(node):
    if len(node.children) > M:
        global root_node
        if node == root_node:
            # If we must split the root node, we need to create a new one.
            new_root = Node(parent=None)
            root_node.parent = new_root
            new_root.children.append(root_node)
            root_node = new_root
        split_node(node)
        adjust_tree(node.parent)


def get_all_split_possibilities(lis):
    # Exhaustive Algorithm
    all_combinations = []
    for r in range(MIN_ELEM, M):  # Excluding 0 and L length, never want that
        comb = []
        for combo in itertools.combinations(lis, r):
            comb.append((combo, set(lis) - set(combo)))
        all_combinations.extend(comb)

    return all_combinations


root_node = Node(parent=None)


def insert_entry(rect):
    entry = TreeEntry(rect, parent=None)
    leafnode = choose_leaf(entry)
    leafnode.children.append(entry)
    entry.parent = leafnode
    adjust_tree(leafnode)
# TODO no re-calculating the entire MBR tree
    root_node.calculate_mbrs()


def search_tree(node, search, out):
    for child in node.children:
        if math_utils.rect_intersects(child.mbr, search):
            out.append(child)
            if not isinstance(child, TreeEntry):
                search_tree(child, search, out)


root_node.children.append(TreeEntry(rect=[1, 1, 2, 2], parent=root_node))
root_node.calculate_mbrs()


def get_leaf_nodes(root, nodes):
    if root.is_leaf():
        nodes.append(root)
    else:
        for child in root.children:
            get_leaf_nodes(child, nodes)


def traverse_tree_and_collect_entries(node, entry_list, node_list):
    node_list.append(node)
    if node.is_leaf():
        entry_list.extend(node.children)
    else:
        for child in node.children:
            traverse_tree_and_collect_entries(child, entry_list, node_list)


import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.ion()

fig, ax, = plt.subplots(figsize=(12, 6))
ax.grid(True)
ax.set_axisbelow(True)
# ax.yaxis.grid(color='gray', linestyle='dashed')
# ax.xaxis.grid(color='gray', linestyle='dashed')
ax.locator_params(nbins=10, tight=True)
# draw
plt.axis('equal')


def draw_rectangles(search_rect):
    ax.clear()
    rectangles = []
    nodes = []
    traverse_tree_and_collect_entries(root_node, rectangles, nodes)
    for ent in rectangles:
        x1, y1, x2, y2 = ent.mbr
        colour = ent.color
        c2 = colour + (0.3,)
        ax.add_patch(patches.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=True, linewidth=2,
                                       edgecolor=colour, facecolor=c2))
        ax.text(x1 + 0.1, y2 - 0.1, str(ent.label), color='black', fontsize=12, va='top', ha='left')

    for node in nodes:
        x1, y1, x2, y2 = node.mbr
        colour = node.color + (0.5,)
        SP = 0.05  # spacer
        ax.add_patch(patches.Rectangle((x1 - SP, y1 - SP), SP * 2 + x2 - x1, SP * 2 + y2 - y1, fill=False, linewidth=2,
                                       linestyle='-',
                                       edgecolor=colour))
        ax.text(x1, y2 - 0.1, node.label, color='black', fontsize=12, va='top', ha='left')

    if search_rect is not None:
        x, y = search_rect[0], search_rect[1]
        w, h = search_rect[2] - search_rect[0], search_rect[3] - search_rect[1]
        ax.add_patch(patches.Rectangle((x, y), w, h, fill=False, linewidth=4,
                                       linestyle='-',
                                       edgecolor=(0,1,0)))
        ax.text(x, y+h-5, 'Search Rect', color='black', fontsize=13, va='top', ha='left')

    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)


for _ in range(50):
    if _ == 8:
        print(str(_))
    x, y = random.randint(0, 1000), random.randint(0, 1000)
    r = [x, y, x + random.randint(1, 100), y + random.randint(1, 100)]
    insert_entry(r)
def paint_search_rects():
    rectangles = []
    nodes = []
    traverse_tree_and_collect_entries(root_node, rectangles, nodes)
    for x in rectangles:
        x.color = (0, 0, 0)
    for y in out:
        y.color = (0,1,0)

SEARCH_RECT_DEMO = True
search = None
if SEARCH_RECT_DEMO:
    search = [500, 400, 800, 800]
    draw_rectangles(None)
    out = []
    search_tree(root_node, search, out)

    paint_search_rects()
draw_rectangles(search_rect=search)

# ETE3 Tree

import draw_tree

draw_tree.from_root(root_node)

while True:
    plt.pause(0.1)
