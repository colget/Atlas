# This Python program uses astroquery to fetch orbital elements for the interstellar comet 3I/ATLAS (C/2025 N1 (ATLAS))
# and the planets Earth, Mars, and Jupiter. It computes their heliocentric positions from August 1, 2025, to March 28, 2026,
# in 5-day steps, highlighting the comet's position on November 1, 2025. The trajectory is animated in 3D using Matplotlib's
# FuncAnimation, showing the comet moving along its path with a marker, relative to the Sun and major planetary orbits.
# Planetary positions are plotted as small circles at each 5-day interval, updated in the animation, without labels as the legend
# clarifies which planet is which. The planetary orbits are approximated as circular in the ecliptic plane for simplicity.
# Font sizes are increased for better visibility.
# Note: The JPL Horizons query uses the provisional designation 'C/2025 N1' for 3I/ATLAS.
# Run this in an environment with astroquery, numpy, and matplotlib installed (e.g., via pip install astroquery numpy matplotlib).

from astroquery.jplhorizons import Horizons
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
from datetime import datetime

# Set global font size for Matplotlib
plt.rcParams.update({'font.size': 10})  # Default font size for all text (axes, ticks, legend)

# Define the comet and planet IDs for Horizons query
obj_id = 'C/2025 N1'  # ATLAS comet, provisional name for 3I/ATLAS
planet_ids = {'Earth': '399', 'Mars': '499', 'Jupiter': '599'}

# Date range: August 1, 2025 to March 28, 2026
start_date = '2025-Nov-01'
stop_date = '2026-Mar-28'
step_size = '2d'  # 5-day steps for smooth trajectory

# Query Horizons for heliocentric positions (observer location=500@0 for Sun center)
# Comet trajectory
traj = Horizons(id=obj_id, location='500@0', epochs={'start': start_date, 'stop': stop_date, 'step': step_size})
vecs = traj.vectors()
x = vecs['x'].data.filled(1e10)  # Convert MaskedColumn to array, fill masked values with large number
y = vecs['y'].data.filled(1e10)  # AU
z = vecs['z'].data.filled(1e10)  # AU

# Query planetary positions
planet_positions = {}
for planet, pid in planet_ids.items():
    planet_traj = Horizons(id=pid, location='500@0', epochs={'start': start_date, 'stop': stop_date, 'step': step_size})
    planet_vecs = planet_traj.vectors()
    planet_positions[planet] = {
        'x': planet_vecs['x'].data.filled(1e10),
        'y': planet_vecs['y'].data.filled(1e10),
        'z': planet_vecs['z'].data.filled(1e10)
    }

# Find index for November 1, 2025
nov1_date = datetime(2025, 11, 1)
start_dt = datetime.strptime(start_date, '%Y-%b-%d')
nov1_index = int((nov1_date - start_dt).days / 2)  # Assuming 5-day steps

# Plot setup: 3D trajectory
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

# Plot static elements: planetary orbits for context (circular, ecliptic plane, Z=0)
theta = np.linspace(0, 2*np.pi, 100)
ax.plot(np.cos(theta), np.sin(theta), np.zeros_like(theta), color='green', linestyle='--', linewidth=1, label='Earth Orbit')
mars_r = 1.35
ax.plot(mars_r * np.cos(theta), mars_r * np.sin(theta), np.zeros_like(theta), color='orange', linestyle='--', linewidth=1, label='Mars Orbit')
jup_r = 5.2
ax.plot(jup_r * np.cos(theta), jup_r * np.sin(theta), np.zeros_like(theta), color='brown', linestyle='--', linewidth=0.5, label='Jupiter Orbit (scaled)')

# Mark the Sun at origin
ax.scatter(0, 0, 0, color='yellow', s=200, label='Sun')

# Highlight comet position on Nov 1, 2025 (static)
ax.scatter(x[nov1_index], y[nov1_index], z[nov1_index], color='red', s=100, label='Position on Nov 1, 2025')

# Initialize animated elements: comet trajectory line and marker
line, = ax.plot([], [], [], label='3I/ATLAS Trajectory', color='blue', linewidth=2)
comet_marker, = ax.plot([], [], [], marker='o', markersize=8, color='blue')

# Initialize animated planetary position markers
planet_markers = {
    'Earth': ax.plot([], [], [], marker='o', markersize=5, color='green')[0],
    'Mars': ax.plot([], [], [], marker='o', markersize=5, color='orange')[0],
    'Jupiter': ax.plot([], [], [], marker='o', markersize=5, color='brown')[0]
}

# Labels and view
ax.set_xlabel('X (AU)', fontsize=6)
ax.set_ylabel('Y (AU)', fontsize=6)
ax.set_zlabel('Z (AU)', fontsize=6)
ax.set_title('Animated Trajectory of Interstellar Comet 3I/ATLAS (C/2025 N1)\nHeliocentric View from Nov 1, 2025 to Mar 28, 2026', fontsize=16)
ax.legend(fontsize=12)  # Slightly smaller legend to balance visibility
ax.view_init(elev=20, azim=45)  # Adjust viewing angle for better perspective

# Set nice symmetric axis limits that always include Jupiter's orbit
# Jupiter ≈ ±5.2 AU, so we force ±6 AU on X and Y (plenty of margin)
# Z remains tighter because the comet and planets stay close to the ecliptic
ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)   # ← this is the line that fixes your request
ax.set_zlim(-2, 2)   # you can keep Z smaller – looks better and the comet never goes far out of plane

# Optional: make it perfectly square and centered (highly recommended for beauty)
ax.set_box_aspect([1, 1, 0.4])  # makes X:Y:Z proportions nice (requires matplotlib ≥3.3)

# Animation function: update the comet trajectory, comet marker, and planetary positions
def update(frame):
    # Update comet trajectory and marker
    line.set_data(x[:frame+1], y[:frame+1])
    line.set_3d_properties(z[:frame+1])
    comet_marker.set_data([x[frame]], [y[frame]])
    comet_marker.set_3d_properties([z[frame]])
    
    # Update planetary positions
    artists = [line, comet_marker]
    for planet, marker in planet_markers.items():
        marker.set_data([planet_positions[planet]['x'][frame]], [planet_positions[planet]['y'][frame]])
        marker.set_3d_properties([planet_positions[planet]['z'][frame]])
        artists.append(marker)
    
    return artists

# Create animation: frames = number of data points, interval=50ms for speed
ani = FuncAnimation(fig, update, frames=len(x), interval=200, blit=False)

# Save as GIF
# print("Saving animation as GIF...")
# gif_writer = PillowWriter(fps=20)
# ani.save('comet_trajectory.gif', writer=gif_writer, dpi=100)
# print("GIF saved as 'comet_trajectory.gif'")


# Save as high-quality slow MP4 (10–15 seconds total)
print("Saving slow high-quality MP4 (this may take 10–30 seconds)...")
mp4_writer = FFMpegWriter(fps=5, bitrate=3000)   # 15 fps → ~13 seconds for your ~190 frames
ani.save('comet_trajectory.mp4', 
         writer=mp4_writer, 
         dpi=150)                                # higher dpi = sharper video
print("MP4 saved as 'comet_trajectory.mp4' – perfect speed for observing orbits!")


#Optionally save as MP4 (uncomment if FFmpeg is installed)
# print("Saving animation as MP4...")
# mp4_writer = FFMpegWriter(fps=20, bitrate=1800)
# ani.save('comet_trajectory.mp4', writer=mp4_writer)
# print("MP4 saved as 'comet_trajectory.mp4'")

# Show the animated plot (optional, for preview)
plt.show()

# Optional: Print comet position on Nov 1, 2025
print(f"Approximate comet position on November 1, 2025: X={x[nov1_index]:.3f} AU, Y={y[nov1_index]:.3f} AU, Z={z[nov1_index]:.3f} AU")
print("Distance from Sun:", np.sqrt(x[nov1_index]**2 + y[nov1_index]**2 + z[nov1_index]**2))