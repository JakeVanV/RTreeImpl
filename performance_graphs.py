import colorsys
import math

import random
import time
from time import sleep
from typing import List

import tqdm
from matplotlib import patches

import draw_tree
import math_utils
import itertools

# PARAMETERS

M = 4
MIN_ELEM = 2

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

        self.color = (0, 0, 0)

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


def linear_pick_seeds(nodes, x_length, y_length):
    # LPS1
    min_x_elem = min(nodes, key=lambda n: n.mbr[0])
    max_x_elem = max(nodes, key=lambda n: n.mbr[2])
    min_y_elem = min(nodes, key=lambda n: n.mbr[1])
    max_y_elem = max(nodes, key=lambda n: n.mbr[3])
    # LPS2
    x_dist = abs(min_x_elem.mbr[2] - max_x_elem.mbr[0])
    y_dist = abs(min_y_elem.mbr[3] - max_y_elem.mbr[1])
    x_dist /= x_length
    y_dist /= y_length

    if min_x_elem == max_x_elem and min_y_elem == max_y_elem:
        # Rare case that happens with crazy bad R-Trees (low M-value with super high clustering)
        return nodes[0], nodes[1]
    if min_x_elem == max_x_elem:
        return min_y_elem, max_y_elem
    if min_y_elem == max_y_elem:
        return min_x_elem, max_x_elem
    # LPS3

    if x_dist < y_dist:
        return min_y_elem, max_y_elem
    else:
        return min_x_elem, max_x_elem


def get_area(rect):
    return (rect[2] - rect[0]) * (rect[3] - rect[1])


def get_mbr(rects):
    return [min(rects, key=lambda n: n.mbr[0]).mbr[0],
            min(rects, key=lambda n: n.mbr[1]).mbr[1],
            max(rects, key=lambda n: n.mbr[2]).mbr[2],
            max(rects, key=lambda n: n.mbr[3]).mbr[3]]


def assign_rects(node_a, node_b, nodes, little_m):
    group_a = [node_a]
    group_b = [node_b]
    nodes.remove(node_a)
    nodes.remove(node_b)
    mbr_a = node_a.mbr
    mbr_b = node_b.mbr

    while len(nodes) > 0:
        # Assign rest of nodes if not enough to fit in m.
        if len(group_a) + len(nodes) <= little_m:
            group_a.extend(nodes)
            mbr_a = get_mbr(group_a)
            break
        if len(group_b) + len(nodes) <= little_m:
            group_b.extend(nodes)
            mbr_b = get_mbr(group_b)
            break

        d1 = 100000000000000000
        d2 = 111111111111111111
        d1_node = None
        d2_node = None
        d1_mbr = None
        d2_mbr = None
        for node in nodes:
            n = node.mbr
            new_mbr_a = [min(n[0], mbr_a[0]), min(n[1], mbr_a[1]), max(n[2], mbr_a[2]), max(n[3], mbr_a[3])]
            new_mbr_b = [min(n[0], mbr_b[0]), min(n[1], mbr_b[1]), max(n[2], mbr_b[2]), max(n[3], mbr_b[3])]

            new_a = get_area(new_mbr_a)
            new_b = get_area(new_mbr_b)

            enlarged_a = new_a - get_area(mbr_a)
            enlarged_b = new_b - get_area(mbr_b)

            if enlarged_a < d1:
                d1 = enlarged_a
                d1_node = node
                d1_mbr = new_mbr_a
            if enlarged_b < d2:
                d2 = enlarged_b
                d2_node = node
                d2_mbr = new_mbr_b

        if d1 < d2:
            to_remove = d1_node
            group_a.append(to_remove)
            mbr_a = d1_mbr
        else:
            to_remove = d2_node
            group_b.append(to_remove)
            mbr_b = d2_mbr
        nodes.remove(to_remove)
    return group_a, group_b, mbr_a, mbr_b


def split_node(node):
    x1, y1, x2, y2 = node.mbr
    emin, emax = linear_pick_seeds(node.children, abs(x1 - x2), abs(y1 - y2))
    group_a, group_b, mbr_a, mbr_b = assign_rects(emin, emax, node.children, MIN_ELEM)

    node.children.clear()
    # Create new node
    node_b = Node(parent=node.parent)
    node_b.parent.children.append(node_b)

    # Clear children
    node.children.clear()
    node_b.children.clear()

    # Add new children
    node.children.extend(group_a)
    node_b.children.extend(group_b)  # 860

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


# RECTANGLE TYPES:

# UNIFORM DIST
def uniform_dist():
    x, y = random.randint(0, 100000), random.randint(0, 100000)
    r = [x, y, x + random.randint(40, 400), y + random.randint(40, 400)]
    return r


# HUGE OVERLAP
def huge_overlap():
    x, y = random.randint(0, 100000), random.randint(0, 100000)
    r = [x, y, x + random.randint(1000, 10000), y + random.randint(1000, 10000)]
    return r


clusters_list = [(random.randint(0, 100000), random.randint(0, 100000)) for _ in range(10)]


def gaussian_clusters():
    x, y = random.choice(clusters_list)
    DIST = 5000
    x += random.gauss(0, DIST)
    y += random.gauss(0, DIST)
    r = [x, y, x + random.randint(10, 2000), y + random.randint(10, 2000)]
    return r


rect_generator = uniform_dist

SHOW_DISTRIBUTIONS = False
if SHOW_DISTRIBUTIONS:
    rects = [rect_generator() for _ in range(3000)]
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    for rect in rects:
        x1, y1, x2, y2 = rect
        ax.add_patch(patches.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=True, linewidth=1,
                                       edgecolor='black', facecolor=(0, 0, 0, 0.1)))
    ax.set_title('Rect_generator: ' + rect_generator.__name__)
    ax.set_xlim(0, 100000)
    ax.set_ylim(0, 100000)
    plt.show()
    exit(1)


# Generate tree
def generate_tree(rect_amount):
    global root_node
    root_node = Node(parent=None)
    root_node.children.append(TreeEntry(rect=[1, 1, 2, 2], parent=root_node))
    root_node.calculate_mbrs()
    for _ in tqdm.tqdm(range(rect_amount), position=2):
        insert_entry(rect_generator())


print("Generating graph data")
graph_data = dict()

import time

for mdiv in tqdm.tqdm(range(5, 70, 20), position=0):
    for M_val in tqdm.tqdm(range(5, 200), position=1, colour='red'):
        M = M_val
        m_val = M_val * (mdiv / 100.0)
        MIN_ELEM = m_val
        # Reset random seed for each test
        random.seed(8)

        # time generation
        tm = time.time()
        generate_tree(6000)
        gen_time = time.time() - tm

        tm = time.time()
        # 1000 queries
        for _ in range(6000):
            search_tree(root_node, rect_generator(), [])
        tm = time.time() - tm

        if mdiv not in graph_data:
            graph_data[mdiv] = []
        M_list = graph_data[mdiv]
        M_list.append((M_val, gen_time, tm))

import matplotlib.pyplot as plt

fig, axs = plt.subplots(2)
colours = dict()
color_pct = 0


def id_to_random_color(i):
    if i not in colours:
        global color_pct
        colours[i] = colorsys.hsv_to_rgb(color_pct, 1, 0.9)
        color_pct += 0.3
    return colours[i]


for m, tpl in graph_data.items():
    M_vals = [s[0] for s in tpl]
    gen_times = [s[1] for s in tpl]
    search_times = [s[2] for s in tpl]

    color = id_to_random_color(m)
    axs[0].scatter(M_vals, gen_times, color=color, label='m: %d%%' % m, linewidths=1, s=5)
    axs[0].plot(M_vals, gen_times, color=color, linestyle='-')

    axs[1].scatter(M_vals, search_times, color=color, label='m: %d%%' % m, linewidths=1, s=5)
    axs[1].plot(M_vals, search_times, color=color, linestyle='-')

# Set labels and a legend
for ax in axs:
    ax.set_xlabel('M-Value')
    ax.set_ylabel('Time (ms)')
    ax.legend(loc='upper right')

axs[0].set_title(rect_generator.__name__ + "\nCreation Time vs M-value")
axs[1].set_title("Search Time vs M-value")

# Show the plot
plt.show()
