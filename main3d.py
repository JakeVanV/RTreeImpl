import colorsys

import random
from typing import List

import tqdm

import itertools

# PARAMETERS

M = 4
MIN_ELEM = 2

label_count = 0


class Rect3d:
    def __init__(self, x1, y1, z1, x2, y2, z2):
        self.x1 = x1
        self.y1 = y1
        self.z1 = z1

        self.x2 = x2
        self.y2 = y2
        self.z2 = z2

    def get_area(self):
        return (self.x2 - self.x1) * (self.y2 - self.y1) * (self.z2 - self.z1)

    def intersect(self, other):
        return not (self.x2 < other.x1 or self.x1 > other.x2 or
                    self.y2 < other.y1 or self.y1 > other.y2 or
                    self.z2 < other.z1 or self.z1 > other.z2)


class TreeEntry:
    def __init__(self, rect, parent):
        self.mbr = rect
        self.parent = parent

        global label_count
        label_count += 1
        self.label = label_count

        self.color = generate_random_color()


random.seed(1)


def calc_mbr(rs: List[Rect3d]):
    x1, y1, z1, x2, y2, z2 = (10000000, 10000000, 10000000, -1, -1, -1)
    for rect in rs:
        x1 = min(x1, rect.x1)
        y1 = min(y1, rect.y1)
        z1 = min(z1, rect.z1)
        x2 = max(x2, rect.x2)
        y2 = max(y2, rect.y2)
        z2 = max(z2, rect.z2)
    return Rect3d(x1, y1, z1, x2, y2, z2)


def generate_random_color():
    return colorsys.hsv_to_rgb(random.random(), 1, 1)


class Node:
    def __init__(self, parent):
        # Non-leaf nodes only
        self.children = []
        self.mbr = Rect3d(-1, -1, -1, -1, -1, -1)

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


def linear_pick_seeds(node):
    # LPS1
    min_x_elem = min(node.children, key=lambda n: n.mbr.x2)
    max_x_elem = max(node.children, key=lambda n: n.mbr.x1)
    min_y_elem = min(node.children, key=lambda n: n.mbr.y2)
    max_y_elem = max(node.children, key=lambda n: n.mbr.y1)
    min_z_elem = min(node.children, key=lambda n: n.mbr.z2)
    max_z_elem = max(node.children, key=lambda n: n.mbr.z1)
    # LPS2 (just gonna delete this for 3d cuz its useless anyway)
    x_length = node.mbr.x2 - node.mbr.x1
    y_length = node.mbr.y2 - node.mbr.y1
    z_length = node.mbr.z2 - node.mbr.z1
    # LPS3
    min_length = min(x_length, y_length, z_length)

    if min_length == x_length:
        return min_x_elem, max_x_elem
    if min_length == y_length:
        return min_y_elem, max_y_elem
    if min_length == z_length:
        return min_z_elem, max_z_elem


def split_node(node):
    # emin, emax = linear_pick_seeds(node)

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
    # Exhaustive Algorithm
    all_combinations = []
    for r in range(MIN_ELEM, M):  # Excluding 0 and L length, never want that
        comb = []
        for combo in itertools.combinations(lis, r):
            comb.append((combo, set(lis) - set(combo)))
        all_combinations.extend(comb)

    return all_combinations


root_node = Node(parent=None)


def insert_entry(rect: Rect3d):
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


def random_rect() -> Rect3d:
    x, y, z = random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)
    return Rect3d(x, y, z,
                  x + random.randint(3, 10), y + random.randint(3, 10), z + random.randint(3, 10))


# Generate tree
def generate_tree():
    global root_node
    root_node = Node(parent=None)
    root_node.children.append(TreeEntry(rect=Rect3d(1, 1, 1, 3, 3, 3), parent=root_node))
    root_node.calculate_mbrs()


generate_tree()


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plt.ion()
def draw_plot():
    ax.clear()
    leafs = []
    nodes = []
    traverse_tree_and_collect_entries(root_node, leafs, nodes)
    for leaf in leafs:
        cube = leaf.mbr
        x1, y1, z1 = cube.x1, cube.y1, cube.z1
        x2, y2, z2 = cube.x2, cube.y2, cube.z2

        points = [
            [x1, y1, z1],
            [x2, y1, z1],
            [x2, y2, z1],
            [x1, y2, z1],
            [x1, y1, z2],
            [x2, y1, z2],
            [x2, y2, z2],
            [x1, y2, z2]
        ]

        faces = [
            [points[0], points[1], points[2], points[3]],
            [points[4], points[5], points[6], points[7]],
            [points[0], points[1], points[5], points[4]],
            [points[2], points[3], points[7], points[6]],
            [points[0], points[3], points[7], points[4]],
            [points[1], points[2], points[6], points[5]]
        ]

        # Make the boxes transparent by changing the alpha value
        face_color = leaf.color + (0.2,)
        ax.add_collection3d(Poly3DCollection(faces, facecolors=face_color, linewidths=1, edgecolors=(0, 0, 0, 0.4)))

    for node in nodes:
        cube = node.mbr
        x1, y1, z1 = cube.x1, cube.y1, cube.z1
        x2, y2, z2 = cube.x2, cube.y2, cube.z2

        points = [
            [x1, y1, z1],
            [x2, y1, z1],
            [x2, y2, z1],
            [x1, y2, z1],
            [x1, y1, z2],
            [x2, y1, z2],
            [x2, y2, z2],
            [x1, y2, z2]
        ]

        faces = [
            [points[0], points[1], points[2], points[3]],
            [points[4], points[5], points[6], points[7]],
            [points[0], points[1], points[5], points[4]],
            [points[2], points[3], points[7], points[6]],
            [points[0], points[3], points[7], points[4]],
            [points[1], points[2], points[6], points[5]]
        ]

        # Make the boxes transparent by changing the alpha value
        face_color = (0, 1, 1, 0)
        ax.add_collection3d(Poly3DCollection(faces, facecolors=face_color, linewidths=1, edgecolors=(0, 0, 0, 0.4)))

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.set_xlim([0, 100])  # Set x-axis limits from -5 to 5
    ax.set_ylim([0, 100])  # Set y-axis limits from -5 to 5
    ax.set_zlim([0, 100])  # Set z-axis limits from -5 to 5

    plt.show()
draw_plot()
# ETE3 Tree

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

