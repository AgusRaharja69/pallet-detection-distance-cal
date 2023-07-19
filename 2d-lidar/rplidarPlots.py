import numpy as np
import matplotlib.pyplot as plt
import json

jsonLidarPath = 'exp-data/lidar/data_18.json'
DMAX: int = 3000
IMIN: int = 0
IMAX: int = 50

# ############ Fix Plot ##############
# # Load Lidar data from JSON file
# with open(jsonLidarPath) as f:
#     lidar_data = json.load(f)

# # Convert data to NumPy arrays
# data = np.array(lidar_data['data'])

# # Extract quality, angle, and range arrays from data
# quality = data[:, 0]
# # angle = data[:, 1]
# angle = np.radians(data[:, 1])
# range = data[:, 2]
# theta_mirrored = np.pi - angle
# print("angle: ", data[:,1])
# print("angle rad: ",angle)
# print("final angle: ", theta_mirrored)
# # Convert polar coordinates to Cartesian coordinates
# # x = range * np.cos(np.radians(angle))
# # y = range * np.sin(np.radians(angle))
# # print(theta_mirrored)
# # Plot Lidar data
# fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
# ax.scatter(theta_mirrored, range, s=1)
# plt.show()
# #######################################
# ############ Life Plot ##############

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

while True:
    # Load Lidar data from JSON file
    with open(jsonLidarPath) as f:
        try :
            lidar_data = json.load(f)
        except:
            lidar_data = {"data": [[0,0,0]]}

    # Convert data to NumPy arrays
    data = np.array(lidar_data['data'])

    # Extract quality, angle, and range arrays from data
    # quality = data[:, 0]
    angle = np.radians(data[:, 1]) # Convert angle to radians
    range = data[:, 2]
    angle = 1.5*np.pi - angle

    # Clear previous plot and plot Lidar data in polar projection
    ax.clear()
    ax.scatter(angle, range, s=5, cmap=plt.cm.Greys_r, lw=0)
    ax.set_rmax(DMAX)
    ax.grid(True)
    plt.draw()
    plt.pause(0.01) # Pause for a short time to update the plot 