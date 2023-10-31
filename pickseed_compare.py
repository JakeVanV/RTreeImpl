import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import tqdm


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

def linear_no_norm(nodes, x_length, y_length):
    # LPS1
    min_x_elem = min(nodes, key=lambda n: n[2])
    max_x_elem = max(nodes, key=lambda n: n[0])
    min_y_elem = min(nodes, key=lambda n: n[3])
    max_y_elem = max(nodes, key=lambda n: n[1])
    # LPS3
    if x_length < y_length:
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


total =1 #100000
full_hits = 0
semi_hits = 0
for xr in tqdm.tqdm(range(total)):
    M = 4
    boxes = []
    xl, yl = random.randint(50, 200), random.randint(50, 200)
    for _ in range(10):
        x, y = random.randint(0, xl), random.randint(0, yl)
        boxes.append((x, y, x + 10, y + 10))

    A = quadratic_pick_seeds(boxes)
    B = diag(boxes, xl, yl)

    if A[0] == B[0] and A[1] == B[1]:
        full_hits += 1
    elif A[0] == B[0] or A[1] == B[1]:
        semi_hits += 1


print("FH %d, SH %d TH %d TFAIL %d" % (full_hits, semi_hits, full_hits+semi_hits, 100000-(full_hits+semi_hits)))

def plot():
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
            edgecolor = (0.7, 0.7, 0.7)
        fillcolor = edgecolor + (0.1,)
        ax.add_patch(patches.Rectangle((x1, y1), width, height, facecolor=fillcolor, edgecolor=edgecolor, linewidth=2))

    x1, y1 = A[0][0]+5, A[0][1]+5
    x2, y2 = A[1][0]+5, A[1][1]+5
    ax.plot([x1, x2], [y1, y2], color='blue', linestyle='-', label='Line between points')
    d = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    ax.annotate(' Quadratic |d|=' + str(int(d)), ((x1+x2) / 2, (y2+y1-10) / 2), color='black')

    x1, y1 = B[0][0] + 5, B[0][1] + 5
    x2, y2 = B[1][0] + 5, B[1][1] + 5
    ax.plot([x1, x2], [y1, y2], color='lime', linestyle='-', label='Line between points')
    d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    ax.annotate(' Linear |d|=' + str(int(d)), ((x1 + x2) / 2, (y2 + y1) / 2), color='black')


    # Annotate the line with a label
    # ax.annotate('Label', ((x1 + x2) / 2, (y1 + y2) / 2), color='blue')


    # Set the axis limits
    ax.set_xlim(0, xl)
    ax.set_ylim(0, yl)
    plt.show()
plot()


