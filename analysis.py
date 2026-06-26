import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

fastf1.Cache.enable_cache('cache')

session = fastf1.get_session(2023, 'Monaco', 'Q')
session.load()

# Get fastest lap for each driver
ver = session.laps.pick_drivers('VER').pick_fastest()
ham = session.laps.pick_drivers('HAM').pick_fastest()

# Get telemetry
ver_tel = ver.get_telemetry().add_distance()
ham_tel = ham.get_telemetry().add_distance()

# --- PLOT 1: Driver Comparison ---
fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
fig.suptitle("VER vs HAM - Monaco 2023 Qualifying", fontsize=14)

axes[0].plot(ver_tel['Distance'], ver_tel['Speed'], color='#0600EF', label='Verstappen')
axes[0].plot(ham_tel['Distance'], ham_tel['Speed'], color='#00D2BE', label='Hamilton')
axes[0].set_ylabel('Speed (km/h)')
axes[0].legend()

axes[1].plot(ver_tel['Distance'], ver_tel['Throttle'], color='#0600EF', label='Verstappen')
axes[1].plot(ham_tel['Distance'], ham_tel['Throttle'], color='#00D2BE', label='Hamilton')
axes[1].set_ylabel('Throttle (%)')
axes[1].legend()

axes[2].plot(ver_tel['Distance'], ver_tel['nGear'], color='#0600EF', label='Verstappen')
axes[2].plot(ham_tel['Distance'], ham_tel['nGear'], color='#00D2BE', label='Hamilton')
axes[2].set_ylabel('Gear')
axes[2].set_xlabel('Distance (m)')
axes[2].legend()

plt.tight_layout()
plt.savefig('ver_vs_ham_monaco.png', dpi=150)
plt.show()

print(f"VER fastest lap: {ver['LapTime']}")
print(f"HAM fastest lap: {ham['LapTime']}")

# --- PLOT 2: Lap Delta ---
ver_dist = ver_tel['Distance'].values
ver_time = ver_tel['Time'].dt.total_seconds().values

ham_dist = ham_tel['Distance'].values
ham_time = ham_tel['Time'].dt.total_seconds().values

# Common distance axis
common_dist = np.linspace(0, min(ver_dist[-1], ham_dist[-1]), 1000)

ver_interp = interp1d(ver_dist, ver_time)(common_dist)
ham_interp = interp1d(ham_dist, ham_time)(common_dist)

delta = ham_interp - ver_interp

fig2, ax = plt.subplots(figsize=(13, 4))
ax.plot(common_dist, delta, color='purple')
ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
ax.fill_between(common_dist, delta, 0, where=(delta > 0), color='#0600EF', alpha=0.3, label='VER faster')
ax.fill_between(common_dist, delta, 0, where=(delta < 0), color='#00D2BE', alpha=0.3, label='HAM faster')
ax.set_xlabel('Distance (m)')
ax.set_ylabel('Delta (seconds)')
ax.set_title('Lap Delta: HAM vs VER - Monaco 2023 Qualifying')
ax.legend()
plt.tight_layout()
plt.savefig('delta_monaco.png', dpi=150)
plt.show()