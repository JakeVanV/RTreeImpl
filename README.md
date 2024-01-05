# RTreeImpl
Implementation for a paper on R-Trees.
See "paper.pdf" for the paper.

## Example: `python3 performance_graphs.py`
![image](https://github.com/JakeVanV/RTreeImpl/assets/60329357/355ec9d7-956e-4ba7-a288-38889bac191c)


# Files
Each file is for a different part of the project:

Main.py: Simple 2d demo - Exhaustive method only. Boolean SEARCH_DEMO controls the search demo

main3d.py: 3d demo - Also exhaustive method only

main_circle: circular demo (Exhaustive only)

math_utils: Utility functions

performance_graphs: Linear/Quadratic/4Axes comparisons. Changing `rect_generator = uniform_dist` to one of the three generator functions to make the graphs shown in the paper

pickseed_compare: Compar 4Axes with linearpickseeds

pickseed_compare_area: Compare 4axes with linearpickseeds (area)

requirements.txt - `pip install -r requirements.txt`

main_raycast: raycast demo
