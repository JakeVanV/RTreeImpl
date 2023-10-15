


def draw_4_box(ax, children_drawn, depth):
    from matplotlib.patches import Rectangle
    bx, by = children_drawn * 20, depth * 10
    ax.add_patch(Rectangle((bx, by), 15, 4, fill=False, color='black', antialiased=False, linewidth=1))

    ax.plot([bx+7.5, bx+7.5], [by, by+4], color='black')
    ax.plot([bx+3.75, bx+3.75], [by, by+4], color='black')
    ax.plot([bx+7.5+3.75, bx+7.5+3.75], [by, by+4], color='black')

def get_parent(root, search_node):
    # Base case: If the root is None or the root itself is the search_node, there's no parent.
    if root is None or root == search_node:
        return None

    for child in root.children:
        if child == search_node:
            return root
        parent = get_parent(child, search_node)
        if parent:
            return parent
    return None

def draw_tree(root, nodes, ax, depth=0):

    # Draw the current node's entries as rectangles
    from matplotlib.patches import Rectangle

    # ax.add_patch(Rectangle((box_x, box_y), 20, 5, fill=False, color='b'))
    # if parent_box_pos is not None:
    #     ax.plot([parent_box_pos[0], box_x+10], [parent_box_pos[1], box_y+5])
    #     ax.text(box_x+1, box_y+4, "R1", color='black', fontsize=12, va='top', ha='left')

    children_drawn = 0
    for node in nodes:
        draw_4_box(ax, children_drawn, depth)
        # ax.add_patch(Rectangle((children_drawn * 20, depth * 10), 15, 4, fill=False, color='black'))
        if node.is_leaf():
            drawn = 0
            for entry in node.entries:
                ax.text(children_drawn * 20 + 0.1 + (drawn*3.75), depth * 10 + 3, entry.label, color='black', fontsize=9, va='top', ha='left')
                drawn += 1
        else:
            drawn = 0
            for child in node.children:
                ax.text(children_drawn * 20 + 0.1 + (drawn * 3.75), depth * 10 + 3, child.label, color='black',
                        fontsize=9, va='top', ha='left')
                drawn += 1
        children_drawn += 1

    if nodes[0] != root:
        parent_nodes = set()
        for node in nodes:
            parent = get_parent(root, node)
            if parent is None:
                parent = get_parent(root, node)
            parent_nodes.add(parent)
        depth += 1
        draw_tree(root, list(parent_nodes), ax, depth)


    # Recursively draw child nodes

    ax.set_aspect('equal')
    ax.set_xlim(-10, 100)
    ax.set_ylim(-10,100)

