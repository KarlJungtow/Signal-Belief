import matplotlib.pyplot as plt
import numpy as np
import random


def create_dot_grid(n_red=120, grid_size=20, dot_size=200, filename="grid.png"):
    # Total dots
    total_dots = grid_size * grid_size

    if n_red > total_dots:
        raise ValueError("Number of red dots exceeds total grid size")

    # Assign colors
    colors = ["blue"] * total_dots
    red_indices = random.sample(range(total_dots), n_red)
    for idx in red_indices:
        colors[idx] = "red"

    # Create grid coordinates
    x, y = np.meshgrid(range(grid_size), range(grid_size))
    x, y = x.flatten(), y.flatten()

    # Plot
    plt.figure(figsize=(6, 6))
    plt.scatter(x, y, c=colors, s=dot_size)
    plt.gca().invert_yaxis()  # Optional: put (0,0) at top-left
    plt.axis("off")
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()

counts = [120, 185, 190, 195, 199, 201, 205, 210, 215, 280]
alph = ["a", "b"]
# Example usage
for elem in alph:
    for count in counts:
        create_dot_grid(n_red=count, filename="static/dots_T0_" + str(count) + "_" + str(elem) + ".png")
