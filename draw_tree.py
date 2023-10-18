from ete3 import Tree, TreeStyle, TextFace, NodeStyle

def tuple_to_hex_color(rgb_tuple):
    # Ensure each value is within the 0-1 range
    r, g, b = [int(min(1, max(0, x)) * 255) for x in rgb_tuple]
    # Convert the values to hexadecimal and format the color string
    hex_color = "#{:02X}{:02X}{:02X}".format(r, g, b)
    return hex_color
def traverse_and_add(t, root):
    child = t.add_child(None, root.label)

    t.add_face(TextFace(root.label), column=0)
    if root.is_leaf():
        for ent in root.children:
            c = child.add_child(None, ent.label)
            style = NodeStyle()
            style['fgcolor'] = tuple_to_hex_color(ent.color)
            c.set_style(style)
            # t.add_face(TextFace(ent.label), column=0)
    else:
        for rc in root.children:
            traverse_and_add(child, rc)

def from_root(root):
    t = Tree("root;")

    traverse_and_add(t, root)



    ts = TreeStyle()
    ts.show_leaf_name = True
    t.show(tree_style=ts)