import cv2
import numpy as np
import yaml
from transforms3d.quaternions import mat2quat

def rmse(objp, imgp, K, D, rvec, tvec):
    predicted, _ = cv2.projectPoints(objp, rvec, tvec, K, D)
    predicted = predicted.squeeze()
    imgp = imgp.squeeze()

    pix_serr = []
    for i in range(len(predicted)):
        xp = predicted[i, 0]
        yp = predicted[i, 1]
        xo = imgp[i, 0]
        yo = imgp[i, 1]
        pix_serr.append((xp - xo) ** 2 + (yp - yo) ** 2)
    ssum = sum(pix_serr)

    return np.sqrt(ssum / len(pix_serr))

def calibrate_camera(config_file, data_file, result_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
        lens = config['lens']
        fx = float(config['fx'])
        fy = float(config['fy'])
        cx = float(config['cx'])
        cy = float(config['cy'])
        k1 = float(config['k1'])
        k2 = float(config['k2'])
        p1 = float(config['p1/k3'])
        p2 = float(config['p2/k4'])

    K = np.array([[fx, 0.0, cx],
                  [0.0, fy, cy],
                  [0.0, 0.0, 1.0]])
    D = np.array([k1, k2, p1, p2])
    print("Camera parameters")
    print("Lens =", lens)
    print("K =")
    print(K)
    print("D =")
    print(D)

    imgp = []
    objp = []
    with open(data_file, 'r') as f:
        for line in f:
            data = line.split()
            objp.append([float(data[0]), float(data[1]), 0.0])
            imgp.append([float(data[2]), float(data[3])])

    imgp = np.array(imgp, dtype=np.float32)
    objp = np.array(objp, dtype=np.float32)

    D_0 = np.array([0.0, 0.0, 0.0, 0.0])
    retval, rvec, tvec = cv2.solvePnP(objp, imgp, K, D_0, flags=cv2.SOLVEPNP_ITERATIVE)
    rmat, _ = cv2.Rodrigues(rvec)

    print("Transform from camera to laser")
    print("T = ")
    print(tvec)
    print("R = ")
    print(rmat)

    print("RMSE in pixel =", rmse(objp, imgp, K, D, rvec, tvec))

    q = mat2quat(rmat)

    with open(result_file, 'w') as f:
        f.write("%f %f %f %f %f %f %f" % (q[0], q[1], q[2], q[3], tvec[0][0], tvec[1][0], tvec[2][0]))

    print("Result output format: qx qy qz qw tx ty tz")

# Usage example
calibrate_camera("config.yaml", "data.txt", "result.txt")