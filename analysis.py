import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt

fastf1.Cache.enable_cache('cache')

session = fastf1.get_session(2023, 'Monaco', 'Q')
session.load()

# Fix: use pick_drivers instead of pick_driver
ver = session.laps.pick_drivers('VER').pick_fastest()
telemetry = ver.get_telemetry()

fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
fig.suptitle("Verstappen Fastest Lap - Monaco 2023 Qualifying", fontsize=14)

axes[0].plot(telemetry['Distance'], telemetry['Speed'], color='red')
axes[0].set_ylabel('Speed (km/h)')

axes[1].plot(telemetry['Distance'], telemetry['Throttle'], color='green')
axes[1].set_ylabel('Throttle (%)')

axes[2].plot(telemetry['Distance'], telemetry['Brake'], color='orange')
axes[2].set_ylabel('Brake')

axes[3].plot(telemetry['Distance'], telemetry['nGear'], color='blue')
axes[3].set_ylabel('Gear')
axes[3].set_xlabel('Distance (m)')

plt.tight_layout()
plt.savefig('monaco_verstappen.png', dpi=150)
plt.show()

print("Plot saved as monaco_verstappen.png")