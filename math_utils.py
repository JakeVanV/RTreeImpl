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
    return abs((rect[0] - rect[2]) * (rect[1] - rect[3]))


def rect_intersects(rect1, rect2):
    return not (rect1[2] < rect2[0] or  # rect1 is to the left of rect2
                rect2[2] < rect1[0] or  # rect2 is to the left of rect1
                rect1[3] < rect2[1] or  # rect1 is above rect2
                rect2[3] < rect1[1])  # rect2 is above rect1

# Str8 outa chatgpt
def intersect_rectangle_ray(rect, ray):
    """
    Checks if a ray intersects with a rectangle.

    Parameters:
    ray (list): A list [x, y, dx, dy] representing the ray's origin and direction.
    rect (list): A list [x1, y1, x2, y2] representing the rectangle's coordinates.

    Returns:
    bool: True if the ray intersects the rectangle, False otherwise.
    """

    # Ray parameters
    rx, ry, rdx, rdy = ray

    # Rectangle parameters
    x1, y1, x2, y2 = rect

    # Ensure that x1,y1 is the lower-left and x2,y2 is the upper-right corners
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    # Ray-Line Intersection function
    def intersects(x3, y3, x4, y4):
        # Lines are defined as p = p1 + t * (p2 - p1), for t in [0,1]
        # Solving for two lines p1 -> p2 and p3 -> p4
        # Return false if the ray and line segment are parallel

        # Ray line
        p1x, p1y = rx, ry
        p2x, p2y = rx + rdx, ry + rdy

        # Rectangle line
        p3x, p3y = x3, y3
        p4x, p4y = x4, y4

        # Denominator for the equations
        den = (p1x - p2x) * (p3y - p4y) - (p1y - p2y) * (p3x - p4x)

        # Parallel lines
        if den == 0:
            return False

        # Solve for t1 and t2
        t1 = ((p1x - p3x) * (p3y - p4y) - (p1y - p3y) * (p3x - p4x)) / den
        t2 = ((p1x - p3x) * (p1y - p2y) - (p1y - p3y) * (p1x - p2x)) / den

        # Check if the intersection point is on both the ray and the line segment
        return 0 <= t2 <= 1 and t1 >= 0

    # Check intersection with each side of the rectangle
    return (
        intersects(x1, y1, x2, y1) or # Bottom side
        intersects(x2, y1, x2, y2) or # Right side
        intersects(x2, y2, x1, y2) or # Top side
        intersects(x1, y2, x1, y1)    # Left side
    )
