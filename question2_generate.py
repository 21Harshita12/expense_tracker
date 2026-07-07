import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def draw_branch(ax, x0, y0, length, angle, depth, max_depth, min_length, theta, s):
    # Termination criteria
    if depth > max_depth or length < min_length:
        return
    
    # Calculate end point of branch segment
    x1 = x0 + length * math.cos(angle)
    y1 = y0 + length * math.sin(angle)
    
    # Color transition: Brown for trunk, green for leaves
    trunk_color = (0.4, 0.25, 0.15)
    leaf_color = (0.1, 0.6, 0.2)
    t = (depth - 1) / max(1, max_depth - 1)
    color = tuple((1 - t) * tc + t * lc for tc, lc in zip(trunk_color, leaf_color))
    
    linewidth = max(0.5, 4.5 * (0.75 ** (depth - 1)))
    
    # Plot branch segment
    ax.plot([x0, x1], [y0, y1], color=color, linewidth=linewidth)
    
    # Recurse child branches
    draw_branch(ax, x1, y1, length * s, angle + theta, depth + 1, max_depth, min_length, theta, s)
    draw_branch(ax, x1, y1, length * s, angle - theta, depth + 1, max_depth, min_length, theta, s)

def main():
    theta = math.pi / 6      # 30 degrees rotation
    s = 0.75                 # scaling factor
    max_depth = 10           # max recursion depth
    min_length = 0.02        # minimum branch length to draw
    
    fig, ax = plt.subplots(figsize=(8, 8), facecolor='#F5F5F5')
    ax.set_facecolor('#F5F5F5')
    
    print("=== DRAWING RECURSIVE FRACTAL TREE ===")
    draw_branch(ax, 0.0, 0.0, 1.0, math.pi / 2, 1, max_depth, min_length, theta, s)
    
    ax.axis('equal')
    ax.axis('off')
    ax.set_title("Recursive Fractal Tree (theta = 30 deg, s = 0.75)", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig("question2_fractal_tree.png", dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    print("Fractal tree rendering saved to question2_fractal_tree.png")

if __name__ == "__main__":
    main()
