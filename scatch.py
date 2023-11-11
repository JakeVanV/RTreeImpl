import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class Rect3d:
    def __init__(self, x1, y1, z1, x2, y2, z2):
        self.x1, self.y1, self.z1 = x1, y1, z1
        self.x2, self.y2, self.z2 = x2, y2, z2

def plot_3d_cubes(cubes):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for cube in cubes:
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
        face_color = (0, 1, 1, 0.2)  # Cyan color with alpha value (0.2 for example)
        ax.add_collection3d(Poly3DCollection(faces, facecolors=face_color, linewidths=1, edgecolors='black'))

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()

# Example usage:
cubes_list = [
    Rect3d(1, 1, 1, 3, 3, 3),
    Rect3d(4, 4, 4, 6, 6, 6),
    Rect3d(2, 2, 2, 5, 5, 5)
]

plot_3d_cubes(cubes_list)