import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def compute_julia(c, N=200, max_iter=100, z_lim=1.5):
    # Setup coordinates
    x = np.linspace(-z_lim, z_lim, N)
    y = np.linspace(-z_lim, z_lim, N)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    M = np.zeros((N, N))
    
    # Calculate Julia set
    for i in range(max_iter):
        mask = np.abs(Z) <= 2.0
        Z[mask] = Z[mask]**2 + c
        M[mask] = i
    return x, y, M

def check_connectivity(c, max_iter=200):
    # Julia set is connected iff the orbit of critical point z=0 is bounded
    z = 0.0j
    for _ in range(max_iter):
        z = z**2 + c
        if abs(z) > 2.0:
            return False  # Disconnected (Cantor dust)
    return True  # Connected

def main():
    # Grid of c values from -0.8 to 0.8 (5x5)
    re_c = np.linspace(-0.8, 0.8, 5)
    im_c = np.linspace(-0.8, 0.8, 5)
    
    fig, axes = plt.subplots(5, 5, figsize=(15, 15), facecolor='#F0F0F0')
    
    print("=== JULIA SET GALLERY ANALYSIS ===")
    print(f"{'Plot':<5} | {'c parameter':<20} | {'Mandelbrot':<12} | {'Connectivity'}")
    print("-" * 60)
    
    plot_idx = 1
    for r in range(5):
        # We index imaginary part from top to bottom (0.8 to -0.8)
        c_imag = im_c[4 - r]
        for col in range(5):
            c_real = re_c[col]
            c = c_real + 1j * c_imag
            
            # Compute Julia set grid
            x, y, M = compute_julia(c)
            
            # Check connectivity
            connected = check_connectivity(c)
            connectivity_str = "Connected" if connected else "Disconnected"
            mandelbrot_str = "Inside" if connected else "Outside"
            
            print(f"{plot_idx:<5} | {c_real: >5.2f} + {c_imag: >5.2f}i | {mandelbrot_str:<12} | {connectivity_str}")
            
            # Plot
            ax = axes[r, col]
            ax.imshow(M, extent=[-1.5, 1.5, -1.5, 1.5], cmap='viridis', origin='lower')
            ax.axis('off')
            ax.set_title(f"c = {c_real:.2f} + {c_imag:.2f}i\n{connectivity_str}", fontsize=9, fontweight='bold')
            
            plot_idx += 1
            
    plt.tight_layout()
    plt.savefig("question3_julia_gallery.png", dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    print("\n5x5 Julia gallery saved successfully as question3_julia_gallery.png")

if __name__ == "__main__":
    main()
