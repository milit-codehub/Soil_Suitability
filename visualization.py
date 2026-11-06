"""
visualization.py - Diagnostic Chart Generation
"""
import matplotlib.pyplot as plt

def generate_diagnostic_plots(df_sorted, df_particles, d10, d50, d60):
    """
    Generates Matplotlib figure containing GSD Cumulative Passing Curve and Particle Area Histogram.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    # Plot 1: Cumulative GSD Curve
    ax1.plot(df_sorted["d_eq_mm"], df_sorted["percent_passing"], color="navy", lw=2, label="Cumulative % Passing")
    ax1.axvline(d10, color="r", linestyle="--", alpha=0.7, label=f"d10={d10:.2f}mm")
    ax1.axvline(d50, color="g", linestyle="--", alpha=0.7, label=f"d50={d50:.2f}mm")
    ax1.axvline(d60, color="orange", linestyle="--", alpha=0.7, label=f"d60={d60:.2f}mm")
    ax1.set_xscale("log")
    ax1.set_xlabel("Particle Diameter d_eq (mm, log scale)")
    ax1.set_ylabel("Cumulative Percent Passing (%)")
    ax1.set_title("Cumulative Grain Size Distribution (GSD)")
    ax1.grid(True, which="both", ls=":", alpha=0.6)
    ax1.legend(fontsize=8)

    # Plot 2: Particle Area Histogram
    ax2.hist(df_particles["Area"], bins=30, color="steelblue", edgecolor="black")
    ax2.set_xlabel("Particle Area (px²)")
    ax2.set_ylabel("Count")
    ax2.set_title("Particle Area Frequency Histogram")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig
