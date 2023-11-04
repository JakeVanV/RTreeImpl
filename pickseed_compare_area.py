import math
import random
import threading
import time

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import tqdm
import numpy as np


def quadratic_pick_seeds(nodes):
    max_elem = None
    max_dist = -1
    for a in nodes:
        for b in nodes:
            dist_sq = (a[0] - b[2]) ** 2 + (a[1] - b[3]) ** 2
            if dist_sq > max_dist:
                max_elem = (a, b)
                max_dist = dist_sq

    return max_elem


def linear_pick_seeds(nodes, x_length, y_length):
    # LPS1
    min_x_elem = min(nodes, key=lambda n: n[2])
    max_x_elem = max(nodes, key=lambda n: n[0])
    min_y_elem = min(nodes, key=lambda n: n[3])
    max_y_elem = max(nodes, key=lambda n: n[1])
    # LPS2
    x_dist = abs(min_x_elem[2] - max_x_elem[0])
    y_dist = abs(min_y_elem[3] - max_y_elem[1])
    x_dist /= x_length
    y_dist /= y_length
    # LPS3
    if x_dist < y_dist:
        return min_y_elem, max_y_elem
    else:
        return min_x_elem, max_x_elem


def diag(nodes, x_length, y_length):
    # LPS1

    min_x_elem = min(nodes, key=lambda n: n[0]+n[1])
    max_x_elem = max(nodes, key=lambda n: n[2]+n[3])

    min_y_elem = min(nodes, key=lambda n: n[0]-n[1])
    max_y_elem = max(nodes, key=lambda n: n[2]-n[3])

    x_dist = (min_x_elem[0] - max_x_elem[2])**2 + (min_x_elem[1] - max_x_elem[3])**2
    y_dist = (min_y_elem[0] - max_y_elem[2])**2 + (min_y_elem[1] - max_y_elem[3])**2

    min_x_elem_f = min(nodes, key=lambda n: n[2])
    max_x_elem_f = max(nodes, key=lambda n: n[0])
    min_y_elem_f = min(nodes, key=lambda n: n[3])
    max_y_elem_f = max(nodes, key=lambda n: n[1])

    x_dist_f = (min_x_elem_f[0] - max_x_elem_f[2]) ** 2 + (min_x_elem_f[1] - max_x_elem_f[3]) ** 2
    y_dist_f = (min_y_elem_f[0] - max_y_elem_f[2]) ** 2 + (min_y_elem_f[1] - max_y_elem_f[3]) ** 2
    # LPS3
    maxd = max(x_dist_f, y_dist_f, x_dist, y_dist)
    if maxd == x_dist:
        return min_x_elem, max_x_elem
    if maxd == y_dist:
        return min_y_elem, max_y_elem
    if maxd == x_dist_f:
        return min_x_elem_f, max_x_elem_f
    if maxd == y_dist_f:
        return min_y_elem_f, max_y_elem_f

def get_area(rect):
    return (rect[2] - rect[0]) * (rect[3] - rect[1])
def get_mbr(rects):
    return [min(rects, key=lambda n: n[0])[0],
            min(rects, key=lambda n: n[1])[1],
            max(rects, key=lambda n: n[2])[2],
            max(rects, key=lambda n: n[3])[3]]

def assign_rects(node_a, node_b, nodes, little_m):
    group_a = [node_a]
    group_b = [node_b]
    nodes.remove(node_a)
    nodes.remove(node_b)
    mbr_a = node_a
    mbr_b = node_b

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
        for n in nodes:
            new_mbr_a = [min(n[0], mbr_a[0]), min(n[1], mbr_a[1]), max(n[2], mbr_a[2]), max(n[3], mbr_a[3])]
            new_mbr_b = [min(n[0], mbr_b[0]), min(n[1], mbr_b[1]), max(n[2], mbr_b[2]), max(n[3], mbr_b[3])]

            new_a = get_area(new_mbr_a)
            new_b = get_area(new_mbr_b)

            enlarged_a = new_a - get_area(mbr_a)
            enlarged_b = new_b - get_area(mbr_b)

            if enlarged_a < d1:
                d1 = enlarged_a
                d1_node = n
                d1_mbr = new_mbr_a
            if enlarged_b < d2:
                d2 = enlarged_b
                d2_node = n
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



# def Linear_assign_rects(node_a, node_b, nodes, little_m):
#     group_a = [node_a]
#     group_b = [node_b]
#     nodes.remove(node_a)
#     nodes.remove(node_b)
#
#     mbr_a = node_a
#     mbr_b = node_b
#     for n in nodes:
#         # Calculate delta size for each group
#         new_mbr_a = [min(n[0], mbr_a[0]), min(n[1], mbr_a[1]), max(n[2], mbr_a[2]), max(n[3], mbr_a[3])]
#         new_mbr_b = [min(n[0], mbr_b[0]), min(n[1], mbr_b[1]), max(n[2], mbr_b[2]), max(n[3], mbr_b[3])]
#
#         new_a = get_area(new_mbr_a)
#         new_b = get_area(new_mbr_b)
#
#         enlarged_a = new_a - get_area(mbr_a)
#         enlarged_b = new_b - get_area(mbr_b)
#
#         if enlarged_a < enlarged_b:
#             group_a.append(n)
#             mbr_a = new_mbr_a
#         elif enlarged_b < enlarged_a:
#             group_b.append(n)
#             mbr_b = new_mbr_b
#         else:
#             if new_a < new_b:
#                 group_a.append(n)
#                 mbr_a = new_mbr_a
#             else:
#                 group_b.append(n)
#                 mbr_b = new_mbr_b
#
#     return group_a, group_b, mbr_a, mbr_b










import _thread


tests_per_mvalue = 10000
MAXVAL = 100
test_results_M = [0 for _ in range(0, MAXVAL)]

test_results_diff = [0 for _ in range(0, MAXVAL)]
data_range = tqdm.tqdm(range(0, MAXVAL), position=0, colour='red')

completed = 0
lock = _thread.allocate_lock()
def run_task_for(nx):
    data_range.set_description("M-value %d" % t)
    full_hits = 0
    semi_hits = 0
    total_area_q = 0
    total_area_l = 0

    M = 4+nx
    m = M//2
    for xr in range(tests_per_mvalue):
    # for xr in tqdm.tqdm(range(tests_per_mvalue), position=1+nx):
        boxes = []
        xl, yl = random.randint(50, 200), random.randint(50, 200)
        for _ in range(M):
            x, y = random.randint(0, xl), random.randint(0, yl)
            boxes.append((x, y, x + 10, y + 10))

        # A = quadratic_pick_seeds(boxes)
        A = linear_pick_seeds(boxes, xl, yl)
        B = diag(boxes, xl, yl)
        q_group_a, q_group_b, q_mbr_a, q_mbr_b = assign_rects(A[0], A[1], list(boxes), m)
        l_group_a, l_group_b, l_mbr_a, l_mbr_b = assign_rects(B[0], B[1], list(boxes), m)

        if A[0] == B[0] and A[1] == B[1]:
            full_hits += 1
        elif A[0] == B[0] or A[1] == B[1]:
            semi_hits += 1

        total_area_q += get_area(q_mbr_a) + get_area(q_mbr_b)
        total_area_l += get_area(l_mbr_a) + get_area(l_mbr_b)
    test_results_M[nx] = M
    # L uses DIAG, Q uses LINEAR or QUADRATIC (comment out A= above)
    test_results_diff[nx] = total_area_q/total_area_l

    # print("FH %d, SH %d TH %d TFAIL %d" % (full_hits, semi_hits, full_hits + semi_hits, 100000 - (full_hits + semi_hits)))
    # print("LA %d, QA %d DIFF %f" % (total_area_l, total_area_q, (total_area_q / total_area_l)))
    lock.acquire()
    global completed
    completed += 1
    print("completed %d" % completed)
    lock.release()

ran = 0
for t in data_range:
    # print("Dispatch Thread %d" % ran)
    # run_task_for(ran)
    _thread.start_new_thread(run_task_for, (ran,))
    ran += 1
while completed != MAXVAL:
   time.sleep(1)

print("all done!!!!")
def plot_graph():
    # Create the bar graph
    plt.bar(test_results_M, test_results_diff, align='center', alpha=0.7, label='% Difference')

    # Calculate and plot the fitted line (regression line)
    z = np.polyfit(test_results_M, test_results_diff, 1)
    p = np.poly1d(z)
    plt.plot(test_results_M, p(test_results_M), "r--", label='Fit Line')

    # Add labels and a legend
    plt.xlabel('Rectangles (M)')
    plt.ylabel('(Linear / 4Axis) %')
    plt.title('How efficient LinearPickSeeds is compared to 4Axis')
    plt.legend()

    # Display the plot
    plt.grid()
    plt.show()

plot_graph()


def plot_demo():
    fig, ax = plt.subplots()

    # Plot each rectangle as a gray patch
    for rect in boxes:
        x1, y1, x2, y2 = rect
        width = x2 - x1
        height = y2 - y1

        is_a = rect == A[0] or rect == A[1]
        is_b = rect == B[0] or rect == B[1]
        if is_a and is_b:
            edgecolor = (1,0,0)
        elif is_a:
            edgecolor = (0, 0, 1)
        elif is_b:
            edgecolor = (0, 1, 0)
        else:
            if rect in l_group_a:
                edgecolor = (0.1, 0.1, 0.7)
            elif rect in l_group_b:
                edgecolor = (0.1, 0.7, 0.1)
            else:
                edgecolor = (0.7, 0.7, 0.7) # error

        fillcolor = edgecolor + (0.1,)
        ax.add_patch(patches.Rectangle((x1, y1), width, height, facecolor=fillcolor, edgecolor=edgecolor, linewidth=2))

    ax.add_patch(patches.Rectangle((l_mbr_a[0], l_mbr_a[1]), (l_mbr_a[2] - l_mbr_a[0]), (l_mbr_a[3] - l_mbr_a[1]), facecolor=(0.1, 0.1, 0.7, 0.1), edgecolor='black', linewidth=2))
    ax.add_patch(patches.Rectangle((l_mbr_b[0], l_mbr_b[1]), (l_mbr_b[2] - l_mbr_b[0]), (l_mbr_b[3] - l_mbr_b[1]), facecolor=(0.1, 0.7, 0.1, 0.1), edgecolor='black', linewidth=2))


    # Annotate the line with a label
    # ax.annotate('Label', ((x1 + x2) / 2, (y1 + y2) / 2), color='blue')


    # Set the axis limits
    ax.set_xlim(0, xl)
    ax.set_ylim(0, yl)
    plt.show()
# plot()


