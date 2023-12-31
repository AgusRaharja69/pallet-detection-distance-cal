import cv2
import numpy as np
import json
import yaml

def get_z(T_cam_world, T_world_pc, K):
    R = T_cam_world[:3, :3]
    t = T_cam_world[:3, 3]
    proj_mat = np.dot(K, np.hstack((R, t[:, np.newaxis])))
    xyz_hom = np.hstack((T_world_pc, np.ones((T_world_pc.shape[0], 1))))
    xy_hom = np.dot(proj_mat, xyz_hom.T).T
    z = xy_hom[:, -1]
    z = np.asarray(z).squeeze()
    return z

def get_proj():
    q = np.array([[ 1.201500e-02, 1.285000e-03, 2.377000e-03, -4.860697e+00],
                  [-1.285000e-03, 1.201500e-02, -9.999240e-01, -7.985340e+00],
                  [-2.377000e-03, 9.999240e-01, 1.201500e-02, 4.365714e+01],
                  [ 0.000000e+00, 0.000000e+00, 0.000000e+00, 1.000000e+00]])
    rvec = np.array([[ 1.55877534],[ 0.00370549],[-0.00200318]])
    tvec = np.array([-4.860697, -7.98534, 43.65714 ])
    K = np.array([[1.86091182e+03, 0.00000000e+00, 3.93702380e+02],
                  [0.00000000e+00, 1.84606954e+03, 4.09530228e+02],
                  [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    D = np.array([-3.12480991e+00, 1.20483327e+02, 7.63097732e-03, -5.64181108e-03])

    jsonLidarPath = "../yolov5-lidar-fusion/exp-data/lidar/data_1.json"  # Replace with the actual path to your LiDAR JSON file

    with open(jsonLidarPath) as f:
        try:
            lidar_data = json.load(f)
        except:
            lidar_data = {"data": [[0, 0, 0]]}
    
    # LiDAR data
    dataLidar = np.array(lidar_data['data'])
    lidar_angles = np.radians(dataLidar[:, 1])  # Convert angle to radians
    lidar_distances = dataLidar[:, 2]  # Lidar distance
    lidar_angles = 1.5*np.pi - lidar_angles

    # Project lidar data into camera frame
    lidar_points = np.zeros((len(lidar_distances), 3))
    for i in range(len(lidar_distances)):
        distance = lidar_distances[i] / 10
        angle = lidar_angles[i]

        x = distance * np.cos(angle)
        y = distance * np.sin(angle)
        z = 10.5 # lidar height 10.5 cm from ground

        lidar_points[i] = [x, y, z]

    Z = get_z(q, lidar_points, K)
    lidar_points = lidar_points[Z > 0]
    img_points, _ = cv2.projectPoints(lidar_points, rvec, tvec, K, D)
    img_points = np.squeeze(img_points)

    # Mirror lidar points vertically
    img_height = 480
    img_points[:, 1] = img_height - img_points[:, 1]

    # Get the current image width
    img_width = 500

    # Calculate the desired center x-coordinate
    center_x_desired = 320

    # Calculate the scaling factor based on the difference between the current and desired center x-coordinates
    scaling_factor = abs(center_x_desired - img_width // 2) / float(img_width // 2)

    # Scale the x-coordinates of img_points
    img_points[:, 0] = img_points[:, 0] * (1.0 - scaling_factor) + center_x_desired * scaling_factor

    return img_points
    

# def callback(image):
#     img = image['data']

#     # Load LiDAR data from lidarJson.json
#     jsonLidarPath = "../lidarJson.json"  # Replace with the actual path to your LiDAR JSON file
#     with open(jsonLidarPath) as f:
#         try:
#             lidar_data = json.load(f)
#         except:
#             lidar_data = {"data": [[0, 0, 0]]}

#     # LiDAR data
#     dataLidar = np.array(lidar_data['data'])
#     lidar_angles = np.radians(dataLidar[:, 1])  # Convert angle to radians
#     lidar_distances = dataLidar[:, 2]  # Lidar distance
#     lidar_angles = 1.5*np.pi - lidar_angles

#     # Project lidar data into camera frame
#     lidar_points = np.zeros((len(lidar_distances), 3))
#     for i in range(len(lidar_distances)):
#         distance = lidar_distances[i] / 10
#         angle = lidar_angles[i]

#         x = distance * np.cos(angle)
#         y = distance * np.sin(angle)
#         z = 10.5 # lidar height 10.5 cm from ground

#         lidar_points[i] = [x, y, z]

#     Z = get_z(q, lidar_points, K)
#     lidar_points = lidar_points[Z > 0]
#     if lens == 'pinhole':
#         img_points, _ = cv2.projectPoints(lidar_points, rvec, tvec, K, D)
#     elif lens == 'fisheye':
#         lidar_points = np.reshape(lidar_points, (1, lidar_points.shape[0], lidar_points.shape[1]))
#         img_points, _ = cv2.fisheye.projectPoints(lidar_points, rvec, tvec, K, D)
#     img_points = np.squeeze(img_points)
    
#     # Mirror lidar points vertically
#     img_height = img.shape[0]
#     try:
#         img_points[:, 1] = img_height - img_points[:, 1]
#     except:
#         # Reshape the img_points array to have two dimensions
#         img_points[1] = img_height - img_points[1]
#         img_points = np.array([img_points])

#     # Get the current image width
#     img_width = 500

#     # Calculate the desired center x-coordinate
#     center_x_desired = 320

#     # Calculate the scaling factor based on the difference between the current and desired center x-coordinates
#     scaling_factor = abs(center_x_desired - img_width // 2) / float(img_width // 2)

#     # Scale the x-coordinates of img_points
#     img_points[:, 0] = img_points[:, 0] * (1.0 - scaling_factor) + center_x_desired * scaling_factor

#     # Draw circles on the image at the locations of the projected lidar points
#     for i in range(len(img_points)):
#         try:
#             center_x = int(round(img_points[i][0]))
#             center_y = int(round(img_points[i][1]))
#             cv2.circle(img, (center_x, center_y), 1, (0, 0, 255), 2)
#         except OverflowError:
#             continue
#     cv2.imshow("Reprojection", img)
#     cv2.waitKey(1)

# # Replace with the actual calibration file path
# calib_file = "result.txt"
# # Replace with the actual config file path
# config_file = "config.yaml"
# # Replace with the desired laser point radius
# laser_point_radius = 1

# # Load camera-to-laser calibration parameters
# with open(calib_file, 'r') as f:
#     data = f.readline().split()
#     qx, qy, qz, qw, tx, ty, tz = map(float, data)
# q = np.array([[qw, -qz, qy, tx],
#               [qz, qw, -qx, ty],
#               [-qy, qx, qw, tz],
#               [0, 0, 0, 1]])
# print("Extrinsic parameter - camera to laser")
# print(q)
# tvec = q[:3, 3]
# rot_mat = q[:3, :3]
# rvec, _ = cv2.Rodrigues(rot_mat)
# print("rvec: ", rvec)
# print("tvec: ", tvec)

# # Load camera parameters from config file
# with open(config_file, 'r') as f:
#     config = yaml.load(f, Loader=yaml.SafeLoader)
#     lens = config['lens']
#     fx = float(config['fx'])
#     fy = float(config['fy'])
#     cx = float(config['cx'])
#     cy = float(config['cy'])
#     k1 = float(config['k1'])
#     k2 = float(config['k2'])
#     p1 = float(config['p1/k3'])
#     p2 = float(config['p2/k4'])

# K = np.array([[fx, 0.0, cx],
#               [0.0, fy, cy],
#               [0.0, 0.0, 1.0]])
# D = np.array([k1, k2, p1, p2])
# print("Camera parameters")
# print("Lens =", lens)
# print("K =")
# print(K)
# print("D =")
# print(D)

# OpenCV VideoCapture for webcam
cap = cv2.VideoCapture(1)  # Replace with the appropriate webcam index if not the default
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # image = {
    #     'data': frame,
    # }
    # callback(image)
    points = get_proj()
    # Draw circles on the image at the locations of the projected lidar points
    for i in range(len(points)):
        try:
            x = int(round(points[i][0]))
            y = int(round(points[i][1]))
            cv2.circle(frame, (x, y), 1, (0, 0, 255), 2)
        except OverflowError:
            continue    
    cv2.imshow("Reprojection", frame)
    cv2.waitKey(1)
cap.release()
cv2.destroyAllWindows()