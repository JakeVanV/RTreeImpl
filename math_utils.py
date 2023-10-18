from typing import List


def calculate_mbr(rects):
    # List of rectangles
    x1, y1, x2, y2 = (10000000, 1000000, -1, -1)
    for rect in rects:
        x1 = min(x1, rect[0])
        y1 = min(y1, rect[1])
        x2 = max(x2, rect[2])
        y2 = max(y2, rect[3])
    return [x1, y1, x2, y2]

def get_area(rect):
    return abs((rect[0]-rect[2]) * (rect[1]-[rect[3]]))
