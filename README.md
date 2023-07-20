# Pallet Detection and Distance Calculation with 2D LiDAR and YOLOv5 Fusion

### Project by AgusRaharja

![Project Icon](https://github.com/AgusRaharja69/pallet-detection-distance-cal/blob/main/yolov5-lidar-fusion/data/icons8-raspberry-pi-zero-96.png)

This project demonstrates the fusion of data from a 2D LiDAR and YOLOv5 for pallet detection and distance calculation. It aims to provide accurate and real-time detection of pallets in a given environment, along with calculating their distances from the sensor.

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [How it Works](#how-it-works)
4. [Contributing](#contributing)
5. [License](#license)
6. [Acknowledgments](#acknowledgments)

## 1. Installation
To set up the project and its dependencies, follow these steps:

```bash
git clone https://github.com/AgusRaharja69/pallet-detection-distance-cal.git
cd pallet-detection-distance-cal
pip install -r requirements.txt
```
## 2. Usage

### Camera Calibration

To calibrate your camera, follow these steps:

1. Navigate to the `camera-calibration` folder:
```bash
cd camera-calibration
```
2. Prepare 7x5 chessboard for calibration 
3. Run camera extrinsic data script:
```bash
python cameraExtrinsic.py
```
4. Run the calibration script or notebook, providing the required input data (e.g., images of calibration patterns) as arguments:
```bash
python calibrationCamera.py
```
5. Naigate to the `yolov5-lidar-fusion`
```bash
cd yolov5-lidar-fusion
```
6. Change this value on `lidarProj.py` based on camera-calibration `config.yaml` and `result.txt`
```bash
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
```
### Object and Distance Detection
7. To use the pallet detection and distance calculation, execute the following command:

```bash
python main.py
```

### Note:
`main.py` can perform video stream and image distance and object detection, just uncommend some line of the code in `yoloDetection.py` and `main.py` 

The script will start processing data from the 2D LiDAR and YOLOv5 model to detect pallets and calculate their distances. The results will be displayed on the terminal or saved to a file, depending on the configuration.

## 3. How it Works
The project utilizes a 2D LiDAR sensor to collect point cloud data from the environment. The LiDAR data is preprocessed and fed into a YOLOv5 object detection model fine-tuned for pallet detection. The model outputs bounding boxes around detected pallets along with their class probabilities.

The fusion algorithm combines the spatial information from the LiDAR data with the object detection results from YOLOv5. By calculating the distance of each detected pallet from the sensor, the system provides accurate distance information for further analysis or control applications.

