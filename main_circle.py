import colorsys
import math

import random
from typing import List

import tqdm

import itertools

# PARAMETERS

M = 4
MIN_ELEM = 2

label_count = 0


class Circle:
    def __init__(self, x1, y1, radius):
        self.x1 = x1
        self.y1 = y1
        self.radius = radius

    def get_area(self):
        return math.pi * (self.radius * self.radius)

    def distance(self, other):
        return math.sqrt((self.x1 - other.x1) ** 2 + (self.y1 - other.y1) ** 2)

    def intersect(self, other):
        return self.distance(other) <= (self.radius + other.radius)


class TreeEntry:
    def __init__(self, rect, parent):
        self.mbr = rect
        self.parent = parent

        global label_count
        label_count += 1
        self.label = label_count

        self.color = generate_random_color()


random.seed(1)
def calc_mbr_old(rs: List[Circle]):
    x1, y1 = 0, 0
    for rect in rs:
        x1 += rect.x1
        y1 += rect.y1
    x1 /= len(rs)
    y1 /= len(rs)
    circ = Circle(x1, y1, 1)
    max_distance_circle = max(rs, key=lambda c: circ.distance(c) + c.radius)
    max_distance = max_distance_circle.distance(circ) + max_distance_circle.radius
    circ.radius = max_distance
    return circ

def calc_mbr(rs: List[Circle]):
    if len(rs) == 1:
        return rs[0]
    if len(rs) == 2:
        x1 = (rs[0].x1 + rs[1].x1)/2
        y1 = (rs[0].y1 + rs[1].y1)/2
        circ = Circle(x1, y1, 1)
        circ.radius = max((circ.distance(rs[0]) + rs[0].radius), (circ.distance(rs[1]) + rs[1].radius))
        return circ
    all_combos = itertools.combinations(rs, 3)
    max_combo = max(all_combos, key=lambda c: c[1].distance(c[0]) + c[1].distance(c[2]) + c[0].distance(c[2])
                                              + c[0].radius + c[1].radius + c[2].radius)
    x1 = (max_combo[0].x1 + max_combo[1].x1 + max_combo[2].x1) / 3
    y1 = (max_combo[0].y1 + max_combo[1].y1 + max_combo[2].y1) / 3

    circ = Circle(x1, y1, 1)
    d1 = circ.distance(max_combo[0]) + max_combo[0].radius
    d2 = circ.distance(max_combo[1]) + max_combo[1].radius
    d3 = circ.distance(max_combo[2]) + max_combo[2].radius
    circ.radius = max(d1, d2, d3)
    return circ
def calc_mbr_DOESNT_WORK(rs: List[Circle]):
    if len(rs) == 1:
        return rs[0]
    all_combos = itertools.combinations(rs, 2)
    max_combo = max(all_combos, key=lambda c: c[1].distance(c[0]) + c[0].radius + c[1].radius)
    x1 = (max_combo[0].x1 + max_combo[1].x1) / 2
    y1 = (max_combo[0].y1 + max_combo[1].y1) / 2

    circ = Circle(x1, y1, 1)
    d1 = circ.distance(max_combo[0]) + max_combo[0].radius
    d2 = circ.distance(max_combo[1]) + max_combo[1].radius
    circ.radius = max(d1, d2)
    return circ



def generate_random_color():
    return colorsys.hsv_to_rgb(random.random(), 1, 1)


class Node:
    def __init__(self, parent):
        # Non-leaf nodes only
        self.children = []
        self.mbr = Circle(-1, -1, 1)

        # Both
        global label_count
        label_count += 1
        self.label = "M" + str(label_count)
        self.parent = parent

        self.color = (0, 0, 0)

    def is_leaf(self) -> bool:
        return isinstance(self.children[0], TreeEntry)

    def is_root(self):
        return self == root_node

    def calculate_mbr_self(self):
        self.mbr = calc_mbr([r3d.mbr for r3d in self.children])

    def calculate_mbrs(self):
        # Calculate MBRs of children first
        if not self.is_leaf():
            for child in self.children:
                child.calculate_mbrs()

        self.mbr = calc_mbr([r3d.mbr for r3d in self.children])

    # based on min axis
    def get_needed_enlargement(self, rect_b):
        enlarged_rect = calc_mbr([self.mbr, rect_b])
        enlarged_area = enlarged_rect.get_area()
        old_area = self.mbr.get_area()

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
        mbr1 = calc_mbr([yx.mbr for yx in child[0]])
        mbr2 = calc_mbr([yx.mbr for yx in child[1]])
        total_size = mbr1.get_area() + mbr2.get_area()
        if total_size <= min_size:
            min_size = total_size
            best_combo = child

    node.children.clear()
    # Create new node
    node_b = Node(parent=node.parent)
    node_b.parent.children.append(node_b)

    node.children.extend(best_combo[0])
    node_b.children.extend(best_combo[1])

    node.calculate_mbr_self()
    node_b.calculate_mbr_self()
    node.parent.calculate_mbr_self()


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
    all_combinations = []
    for r in range(MIN_ELEM, M):  # Excluding 0 and L length, never want that
        comb = []
        for combo in itertools.combinations(lis, r):
            comb.append((combo, set(lis) - set(combo)))
        all_combinations.extend(comb)

    return all_combinations


root_node = Node(parent=None)


def insert_entry(rect: Circle):
    entry = TreeEntry(rect, parent=None)
    leafnode = choose_leaf(entry)
    leafnode.children.append(entry)
    entry.parent = leafnode
    adjust_tree(leafnode)
    # TODO no re-calculating the entire MBR tree
    root_node.calculate_mbrs()


def search_tree(node, search, out):
    for child in node.children:
        if search.intersects(node.mbr):
            out.append(child)
            if not isinstance(child, TreeEntry):
                search_tree(child, search, out)


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


def random_rect() -> Circle:
    x, y, r = random.randint(0, 100), random.randint(0, 100), random.randint(1, 2)
    return Circle(x, y, r)


# Generate tree
def generate_tree():
    global root_node
    root_node = Node(parent=None)
    root_node.children.append(TreeEntry(rect=Circle(1, 1, 3), parent=root_node))
    root_node.calculate_mbrs()


generate_tree()

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

fig, ax = plt.subplots()
plt.ion()

def draw_plot():
    ax.clear()
    leafs = []
    nodes = []
    traverse_tree_and_collect_entries(root_node, leafs, nodes)

    for leaf in leafs:
        circle = leaf.mbr
        colour = leaf.color + (0.3,)
        circle_obj = plt.Circle((circle.x1, circle.y1), circle.radius, color=colour, fill=True, linestyle='--')
        ax.add_patch(circle_obj)
    for leaf in nodes:
        ONLY_SHOW_LAST_MB_CIRCLES = False
        if ONLY_SHOW_LAST_MB_CIRCLES:
            if not isinstance(leaf.children[0], TreeEntry):
                continue
        circle = leaf.mbr
        colour = (0, 0, 0, 0.7)
        circle_obj = plt.Circle((circle.x1, circle.y1), circle.radius, color=colour, fill=False, linestyle='--')
        ax.add_patch(circle_obj)

    ax.set_aspect('equal')  # Set aspect ratio to be equal to avoid distortion

    plt.xlim(-50, 150)  # Adjust the plot limits for better visualization
    plt.ylim(-50, 150)

    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Circles')

    plt.show()


draw_plot()

import draw_tree
import sys


def on_press(event):
    print('press', event.key)
    sys.stdout.flush()
    if event.key == 'n':
        insert_entry(random_rect())
        draw_plot()
        fig.canvas.draw()
    if event.key == 'm':
        draw_tree.from_root(root_node)


fig.canvas.mpl_connect('key_press_event', on_press)


while True:
    plt.pause(0.1)
