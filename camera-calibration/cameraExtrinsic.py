import cv2
import numpy as np
import yaml

# Calibration parameters - adjust according to your setup
lidar_height = 10.5  # cm
camera_height = 14.5  # cm
image_width = 640
image_height = 480
chessboard_size = (7, 5)  # Number of inner corners in the pattern

# Capture and calibrate the camera
cap = cv2.VideoCapture(1)  # Adjust camera index if needed

objpoints = []  # 3D points in the real-world coordinate system
imgpoints = []  # 2D points in the camera image coordinate system

while len(objpoints) < 50:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    if ret:
        objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

        objpoints.append(objp)
        imgpoints.append(corners)

        cv2.drawChessboardCorners(frame, chessboard_size, corners, ret)
        cv2.imshow('Chessboard', frame)
        cv2.waitKey(500)  # Delay to visualize the detected corners

cv2.destroyAllWindows()

# Calibrate the camera
ret, camera_matrix, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, (image_width, image_height), None, None)


print("camera_matrix: ", camera_matrix)
print("rvecs: ", rvecs)
print("tvecs: ", tvecs)
print("dist: ", dist)

# Save camera parameters to config.yaml
config_data = {
    'lens': 'pinhole',
    'fx': float(camera_matrix[0,0]),
    'fy': float(camera_matrix[1,1]),
    'cx': float(camera_matrix[0,2]),
    'cy': float(camera_matrix[1,2]),
    'k1': float(dist[0,0]),
    'k2': float(dist[0,1]),
    'p1/k3': float(dist[0,2]),
    'p2/k4': float(dist[0,3])
}

with open('config.yaml', 'w') as f:
    yaml.dump(config_data, f)

# Save calibration data to data.txt
with open('data.txt', 'w') as f:    
    for i in range(len(objpoints)):
        for j in range(len(objpoints[i])):
            line = f"{objpoints[i][j][0]} {objpoints[i][j][1]} {imgpoints[i][j][0][0]} {imgpoints[i][j][0][1]}\n"
            f.write(line)

cap.release()