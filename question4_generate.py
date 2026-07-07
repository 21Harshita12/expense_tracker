import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

def compute_mandelbrot_vectorized(x_center, y_center, zoom_val, max_iter, N=800):
    # Vectorized computation using NumPy matrices
    width = 3.0 / zoom_val
    height = 2.5 / zoom_val
    
    x = np.linspace(x_center - width/2, x_center + width/2, N)
    y = np.linspace(y_center - height/2, y_center + height/2, N)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    
    Z = np.zeros_like(C)
    M = np.zeros_like(C, dtype=float)
    
    # Vectorized iteration loop (no loops over pixels)
    for i in range(max_iter):
        mask = (Z.real**2 + Z.imag**2) <= 4.0
        Z[mask] = Z[mask]**2 + C[mask]
        M[mask] = i
        
    return x, y, M

def main():
    x_center = -0.7
    y_center = 0.0
    zoom_val = 1.0
    max_iter = 100
    
    # Create the figure layout with space for sliders on the right
    # (Matches the uicontrol structure of the MATLAB figure)
    fig = plt.figure(figsize=(12, 8), facecolor='#F5F5F5')
    
    # Main plot axes
    ax_plot = fig.add_axes([0.08, 0.12, 0.55, 0.75])
    
    # Compute vectorized Mandelbrot
    print("=== COMPUTING VECTORIZED MANDELBROT ===")
    x, y, M = compute_mandelbrot_vectorized(x_center, y_center, zoom_val, max_iter)
    
    # Plot using a perceptually uniform colormap 'viridis' (matches 'parula' in visual characteristics)
    im = ax_plot.imshow(M, extent=[x.min(), x.max(), y.min(), y.max()], cmap='viridis', origin='lower')
    ax_plot.set_xlabel("Re(c)")
    ax_plot.set_ylabel("Im(c)")
    ax_plot.set_title(f"Vectorized Mandelbrot Set (Zoom: {zoom_val}x, Max Iter: {max_iter})", fontsize=12, fontweight='bold')
    fig.colorbar(im, ax=ax_plot, fraction=0.046, pad=0.04)
    
    # Add dummy slider boxes to mimic the MATLAB uicontrol UI interface in the static image
    slider_bg = '#E0E0E0'
    ax_title = fig.add_axes([0.72, 0.82, 0.22, 0.05])
    ax_title.axis('off')
    ax_title.text(0.5, 0.5, "Interactive Controls", fontsize=12, fontweight='bold', ha='center', va='center')
    
    # X Center Slider representation
    ax_x = fig.add_axes([0.72, 0.70, 0.22, 0.03], facecolor=slider_bg)
    s_x = Slider(ax_x, 'Re Center', -2.0, 0.5, valinit=x_center)
    
    # Y Center Slider representation
    ax_y = fig.add_axes([0.72, 0.58, 0.22, 0.03], facecolor=slider_bg)
    s_y = Slider(ax_y, 'Im Center', -1.25, 1.25, valinit=y_center)
    
    # Zoom Slider representation
    ax_zoom = fig.add_axes([0.72, 0.46, 0.22, 0.03], facecolor=slider_bg)
    s_zoom = Slider(ax_zoom, 'Zoom Factor', 0.5, 20.0, valinit=zoom_val)
    
    # Max Iter Slider representation
    ax_iter = fig.add_axes([0.72, 0.34, 0.22, 0.03], facecolor=slider_bg)
    s_iter = Slider(ax_iter, 'Max Iter', 10, 300, valinit=max_iter, valfmt='%d')
    
    # Add some descriptive notes about sensitivity
    ax_notes = fig.add_axes([0.72, 0.12, 0.22, 0.16])
    ax_notes.axis('off')
    ax_notes.text(0.0, 1.0, "Real-time Sensitivity Notes:\n- Adjusting Re/Im shifts coordinates.\n- Increasing Zoom reveals finer structures.\n- Increasing Max Iter improves boundary detail.", 
                  fontsize=9, color='#333333', va='top')
    
    # Save as high-resolution PNG (300 DPI)
    plt.savefig("mandelbrot_vectorized.png", dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    print("Vectorized Mandelbrot saved to mandelbrot_vectorized.png (DPI=300)")

if __name__ == "__main__":
    main()
