import numpy as np
import matplotlib.pyplot as plt

relative_points = {
    "a": np.array([0, 35]),
    "b": np.array([8, 40]),
    "c": np.array([16, 35]),
    "d": np.array([16, -10]),
    "e": np.array([0, -10]),
    "chute": np.array([8, -10]),
}

plt.figure(figsize=(6,8))

# plot titik-titik utama
for name, point in relative_points.items():
    x, y = point
    plt.scatter(x, y)
    plt.text(x + 0.3, y + 0.3, name)

# gambar origin (0,0)
plt.scatter(0, 0, s=100, marker='o')
plt.text(0.3, 0.3, "(O)")

# outline bentuk
outline_order = ["e", "a", "b", "c", "d", "chute", "e"]

outline_x = [relative_points[k][0] for k in outline_order]
outline_y = [relative_points[k][1] for k in outline_order]

plt.plot(outline_x, outline_y)

plt.xlabel("X Position (m)")
plt.ylabel("Y Position (m)")
plt.title("Relative Point Layout (meter)")

plt.grid(True)

# HILANGKAN garis sumbu origin
# hapus plt.axhline(0)
# hapus plt.axvline(0)

plt.axis("equal")

plt.show()