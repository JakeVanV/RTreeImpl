import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class Node:
    def __init__(self):
        self.children = []

def draw_tree(node, ax, x, y, width, height, depth):
    if not node:
        return

    # Draw the current node as a rectangle
    ax.add_patch(Rectangle((x, y), width, height, fill=False, color='b'))

    # Calculate the width for child nodes
    child_width = width / len(node.children) if node.children else width

    # Recursively draw child nodes
    for i, child in enumerate(node.children):
        child_x = x + i * child_width
        draw_tree(child, ax, child_x, y - height - depth, child_width, height, depth)

# Create a structured tree
root_node = Node()
child1 = Node()
child2 = Node()
child3 = Node()

root_node.children.extend([child1, child2, child3])

child1_1 = Node()
child1_2 = Node()
child1.children.extend([child1_1, child1_2])

# Create a Matplotlib figure and axis
fig, ax = plt.subplots()

# Set the size of the figure
fig.set_size_inches(6, 4)

# Draw the tree starting from the root node
draw_tree(root_node, ax, x=0, y=0, width=1, height=0.2, depth=0.2)

# Set the aspect ratio to 'equal' for a better visualization
ax.set_aspect('equal')

# Set axis limits
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# Show the plot
plt.show()