import os
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# Paths
# =====================================================

BASE = os.path.expanduser("~/Desktop/BOX_PLOTS_DATA")

paths = {
    "Husky Horizontal": os.path.join(BASE, "husky horizontal", "Husky_like_robot&controllers.csv"),
    "Husky-like Horizontal": os.path.join(BASE, "husky_like_horizontal", "Husky_like_robot&controllers.csv"),
    "Laikago Horizontal": os.path.join(BASE, "laikago horizontal", "Husky_like_robot&controllers.csv"),

    "Husky Mars": os.path.join(BASE, "husky marte", "Husky_like_robot&controllers.csv"),
    "Husky-like Mars": os.path.join(BASE, "husky_like_marte", "Husky_like_robot&controllers.csv"),
    "Laikago Mars": os.path.join(BASE, "laikago marte", "Husky_like_robot&controllers.csv")
}

dfs = {name: pd.read_csv(path) for name, path in paths.items()}

# =====================================================
# Convert timesteps to seconds
# =====================================================

SECONDS_PER_STEP = 20.0 / 4800.0

plt.rcParams.update({
    "font.size": 14,
    "axes.spines.top": False,
    "axes.spines.right": False
})

# =====================================================
# Common boxplot style
# =====================================================

boxprops = dict(
    facecolor="lightgray",
    linewidth=1.8
)

medianprops = dict(
    color="darkorange",
    linewidth=2.5
)

whiskerprops = dict(linewidth=1.6)

capprops = dict(linewidth=1.6)

flierprops = dict(
    marker='o',
    markerfacecolor='gray',
    markeredgecolor='gray',
    markersize=4,
    alpha=0.6
)

# =====================================================
# Horizontal Distance
# =====================================================

plt.figure(figsize=(8,6))

plt.boxplot(
    [
        dfs["Husky Horizontal"]["Distance"],
        dfs["Husky-like Horizontal"]["Distance"],
        dfs["Laikago Horizontal"]["Distance"]
    ],
    labels=["Husky", "Husky-like", "Laikago"],
    patch_artist=True,
    boxprops=boxprops,
    medianprops=medianprops,
    whiskerprops=whiskerprops,
    capprops=capprops,
    flierprops=flierprops
)

plt.ylabel("Distance travelled (m)")
plt.title("Distance travelled on horizontal terrain")

plt.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.savefig("horizontal_distance_boxplot.png", dpi=300)

# =====================================================
# Martian Distance
# =====================================================

plt.figure(figsize=(8,6))

plt.boxplot(
    [
        dfs["Husky Mars"]["Distance"],
        dfs["Husky-like Mars"]["Distance"],
        dfs["Laikago Mars"]["Distance"]
    ],
    labels=["Husky", "Husky-like", "Laikago"],
    patch_artist=True,
    boxprops=boxprops,
    medianprops=medianprops,
    whiskerprops=whiskerprops,
    capprops=capprops,
    flierprops=flierprops
)

plt.ylabel("Distance travelled (m)")
plt.title("Distance travelled on Martian terrain")

plt.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.savefig("mars_distance_boxplot.png", dpi=300)

# =====================================================
# Horizontal Episode Duration
# =====================================================

plt.figure(figsize=(8,6))

plt.boxplot(
    [
        dfs["Husky Horizontal"]["Steps"] * SECONDS_PER_STEP,
        dfs["Husky-like Horizontal"]["Steps"] * SECONDS_PER_STEP,
        dfs["Laikago Horizontal"]["Steps"] * SECONDS_PER_STEP
    ],
    labels=["Husky", "Husky-like", "Laikago"],
    patch_artist=True,
    boxprops=boxprops,
    medianprops=medianprops,
    whiskerprops=whiskerprops,
    capprops=capprops,
    flierprops=flierprops
)

plt.axhline(
    20,
    color="red",
    linestyle="--",
    linewidth=2
)

plt.ylabel("Episode duration (s)")
plt.title("Episode duration on horizontal terrain")

plt.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.savefig("horizontal_time_boxplot.png", dpi=300)

# =====================================================
# Martian Episode Duration
# =====================================================

plt.figure(figsize=(8,6))

plt.boxplot(
    [
        dfs["Husky Mars"]["Steps"] * SECONDS_PER_STEP,
        dfs["Husky-like Mars"]["Steps"] * SECONDS_PER_STEP,
        dfs["Laikago Mars"]["Steps"] * SECONDS_PER_STEP
    ],
    labels=["Husky", "Husky-like", "Laikago"],
    patch_artist=True,
    boxprops=boxprops,
    medianprops=medianprops,
    whiskerprops=whiskerprops,
    capprops=capprops,
    flierprops=flierprops
)

plt.axhline(
    20,
    color="red",
    linestyle="--",
    linewidth=2
)

plt.ylabel("Episode duration (s)")
plt.title("Episode duration on Martian terrain")

plt.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.savefig("mars_time_boxplot.png", dpi=300)

# =====================================================
# Show all figures
# =====================================================

plt.show()