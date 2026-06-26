import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt

fastf1.Cache.enable_cache('cache')

session = fastf1.get_session(2023, 'Monaco', 'Q')
session.load()

# Get fastest lap for each driver
ver = session.laps.pick_drivers('VER').pick_fastest()
ham = session.laps.pick_drivers('HAM').pick_fastest()

# Get telemetry
ver_tel = ver.get_telemetry().add_distance()
ham_tel = ham.get_telemetry().add_distance()

fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
fig.suptitle("VER vs HAM - Monaco 2023 Qualifying", fontsize=14)

# Speed comparison
axes[0].plot(ver_tel['Distance'], ver_tel['Speed'], color='#0600EF', label='Verstappen')
axes[0].plot(ham_tel['Distance'], ham_tel['Speed'], color='#00D2BE', label='Hamilton')
axes[0].set_ylabel('Speed (km/h)')
axes[0].legend()

# Throttle comparison
axes[1].plot(ver_tel['Distance'], ver_tel['Throttle'], color='#0600EF', label='Verstappen')
axes[1].plot(ham_tel['Distance'], ham_tel['Throttle'], color='#00D2BE', label='Hamilton')
axes[1].set_ylabel('Throttle (%)')
axes[1].legend()

# Gear comparison
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