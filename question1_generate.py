import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def mandelbrot_pixel_loops(N, max_iter=100):
    # Setup coordinates
    x = np.linspace(-2.0, 0.5, N)
    y = np.linspace(-1.25, 1.25, N)
    M = np.zeros((N, N))
    
    # Nested loops to match the original MATLAB algorithm structure
    for i in range(N):
        cy = y[i]
        for j in range(N):
            cx = x[j]
            c = cx + 1j * cy
            z = 0.0j
            iter_count = 0
            while abs(z) <= 2.0 and iter_count < max_iter:
                z = z*z + c
                iter_count += 1
            M[i, j] = iter_count
    return x, y, M

def main():
    resolutions = [400, 800, 1600]
    times = []
    results = []
    
    print("=== MANDELBROT RESOLUTION COMPARISON (PYTHON) ===")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, N in enumerate(resolutions):
        print(f"Rendering resolution {N}x{N}... ", end="", flush=True)
        start_time = time.time()
        x, y, M = mandelbrot_pixel_loops(N)
        elapsed = time.time() - start_time
        times.append(elapsed)
        print(f"Completed in {elapsed:.4f} seconds.")
        
        # Plot with perceptually uniform colormap 'viridis' (similar to 'parula' in Matlab)
        im = axes[idx].imshow(M, extent=[-2.0, 0.5, -1.25, 1.25], cmap='viridis', origin='lower')
        axes[idx].set_title(f"Resolution: {N} x {N}\nTime: {elapsed:.4f} s", fontsize=12, fontweight='bold')
        axes[idx].set_xlabel("Re(c)")
        axes[idx].set_ylabel("Im(c)")
        fig.colorbar(im, ax=axes[idx], fraction=0.046, pad=0.04)
        
    plt.tight_layout()
    plt.savefig("question1_mandelbrot_comparison.png", dpi=300)
    print("\nTiming Summary:")
    for N, t in zip(resolutions, times):
        print(f"Resolution {N}x{N}: {t:.4f} seconds")

if __name__ == "__main__":
    main()
