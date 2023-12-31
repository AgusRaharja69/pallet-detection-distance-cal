from yoloDetection import run
from lidarProj import get_proj
import cv2
import numpy as np
import json
# import platform # When using Linux

weights_name = "yolov5m-100"
cv_font = cv2.FONT_HERSHEY_SIMPLEX
jsonLidarPath = "exp-data/lidar/data_9.json"
angle, lidarDist = [], []

''' Euclidean '''
def compute_euclidean(x, y):
    return np.sqrt(np.sum((x-y)**2))

''' Find focal length of camera using Triangle Similiarity Principle on Pinhole Camera Model '''
def focal_length(xy,confidence):       
    # RESULT (yolom = 952.69, yolos = 989.057, yolon = 975.829)
    W = 50 # width of knowing object
    D = 100 # distance from camera
    P = int(xy[2] - xy[0])
    F = round(P*D/W, 3)
    fUse = 0
    if confidence > 0.5:
        fUse = F
        # print("Focal Length: ", fUse)
    return F, fUse

''' Find distance using Triangle Similiarity Principle on Pinhole Camera Model '''
def dist_pinhole(xy,X,Y,im0_shape,confidence):
    W = 50
    F = 952.69 if weights_name == 'yolov5m-100' else 989.057 if weights_name == 'yolov5s-100' else 975.829
    D = None

    if confidence > 0.5:
        # print("xy: ",xy)
        # print("X: ", X)
        # print("Y: ", Y)
        # print("imShape: ",im0_shape)
        # print("====================================") 
        P = int(xy[2] - xy[0])
        CenterD = W * F / P  # center distance
        dA = np.array((X, Y))
        dB = np.array((int(im0_shape / 2), Y))
        wA = np.array(p1)
        wB = np.array((int(xy[2]), int(xy[1])))
        SideD = (compute_euclidean(dA, dB) / compute_euclidean(wA, wB)) * W  # Find the distance of center object to center frame
        D = round(np.hypot(CenterD, SideD), 3)
        # print("Distance: ",D)
    return D

''' Find distance using 2D LiDAR camera fusion with angle similiarity '''
def dist_lidar(xy,im0_shape,confidence):
    ''' Opening LiDAR data '''  
    with open(jsonLidarPath) as f:
        try :
            lidar_data = json.load(f)
        except:
            lidar_data = {"data": [[0,0,0]]}
    D = None
    
    if confidence > 0.5:
        # LiDAR data
        dataLidar = np.array(lidar_data['data'])
        angleRawLidar = np.radians(dataLidar[:, 1]) # Convert angle to radians
        rangeLidar = dataLidar[:, 2]
        angleLidar = 1.5*np.pi - angleRawLidar #mirror

        # print(angleLidar)

        # Angle by camera
        FoV = 50
        dispPix = int(im0_shape)

        detectWidth = round(int(xy[2] - xy[0])/5)
        AnglePix = [int(xy[0]),(int(xy[0])+detectWidth),(int(xy[2])-detectWidth),int(xy[2])]
        angleCamDet = [x*(FoV/dispPix) for x in AnglePix]
        angleCam = np.radians([90 + (FoV/2) - x for x in angleCamDet])

        # print(angleCam)

        # Scan dist
        angleArrayId = np.where(((angleLidar >= angleCam[1]) & (angleLidar <= angleCam[0])) | ((angleLidar >= angleCam[3]) & (angleLidar <= angleCam[2])))[0]
        # print(angleArrayId)
        D = np.median([rangeLidar[x] for x in angleArrayId])/10   
        # D = lidarDist
    return D

''' Main Program '''
for im0, det in run():    
    ''' Write results '''
    for *xyxy, conf, cls in reversed(det):
        lw = 1
        txt_color = (255, 255, 255)
        color = (10, 15, 255)
        label = f'{"Wooden-Pallet"} {conf:.2f}'

        p1, p2 = (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3]))
        cv2.rectangle(im0, p1, p2, color, thickness=lw, lineType=cv2.LINE_AA)
        if label:
            tf = max(lw - 1, 1)  # font thickness
            w, h = cv2.getTextSize(label, 0, fontScale=lw / 3, thickness=tf)[0]  # text width, height
            outside = p1[1] - h >= 3
            p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
            cv2.rectangle(im0, p1, p2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(im0,
                        label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),
                        0,
                        lw / 3,
                        txt_color,
                        thickness=tf,
                        lineType=cv2.LINE_AA)
        x = int((xyxy[0] + xyxy[2]) / 2)
        y = int((xyxy[1] + xyxy[3]) / 2)

        ''' Edit Display Camera '''
        # coordinate_text = "(" + str(round(x)) + "," + str(round(y)) + ")" # pixel coordinate
        # cv2.putText(im0, text=coordinate_text, org=(x, y), # center coordinate pixel value
        # fontFace = cv_font, fontScale = 0.7, color=(255,255,255), thickness=1, lineType = cv2.LINE_AA)
        # cv2.circle(im0, (x, y), 5, (0, 255, 0), -1)  # center coordinate
        # cv2.circle(im0,(int(im0.shape[1]/2),int(im0.shape[0]/2)), 5, (0,255,255), -1) # center frame
        # cv2.line(im0, (x, 0), (x, imgsz[1]), (0, 100, 0), thickness=2) # vertical line
        # cv2.circle(im0,(int(xyxy[0]), int(xyxy[1])), 5, (0,255,0), -1) # start coordinate
        # cv2.circle(im0,(int(xyxy[2]), int(xyxy[3])), 5, (255,0,0), -1) # end coordinate
        cv2.putText(im0, text="weights model : " + weights_name, org=(15, 20),  # weights names
        fontFace=cv_font, fontScale=0.6, color=(255, 55, 25), thickness=1, lineType=cv2.LINE_AA)

        ''' Find Object Distance Using Triangle Similiarity'''
        # dist = dist_pinhole(xyxy,x,y,im0.shape[1],conf)

        ''' Find Object Distance Using Angle and DFOV'''
        # dist = dist_lidar(xyxy,im0.shape[1],conf)

        ''' Find Object Distance Using LiDAR projection'''
        points, distances = get_proj(jsonLidarPath)
        pointDetect = []
        for i in range(len(points)):
            try:
                x = int(round(points[i][0]))
                y = int(round(points[i][1]))
                if x>=xyxy[0] and x<= xyxy[2] :
                    pointDetect.append(i)
                cv2.circle(im0, (x, y), 1, (5, 255, 5), 2)
            except OverflowError:
                continue        
        dist = np.min([distances[x] for x in pointDetect])/10

        cv2.putText(im0, text=str(dist) + "cm", org=(p2[0]+20, p1[1]+5),  # distance
        fontFace=cv_font, fontScale=0.5, color=(0, 255, 0), thickness=1, lineType=cv2.LINE_AA)

    ''' Stream results '''    # uncommend if using webcam
        # if platform.system() == 'Linux' and p not in windows:
        #     windows.append(p)
        #     cv2.namedWindow(str(p), cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)  # allow window resize (Linux)
        #     cv2.resizeWindow(str(p), im0.shape[1], im0.shape[0])
        # cv2.imshow(str(1), im0)
        # key = cv2.waitKey(1)  # 1 millisecond

    ''' Stream results '''    # uncommend if using image Path
    im0 = np.asarray(im0)
    while(len(im0)==480):        
        cv2.imshow(str(1), im0)
        key = cv2.waitKey(1)  # 1 millisecond
        if key == ord('s'):
            from pathlib import Path
            image_dir = Path("exp-data/images/detect")
            nb_files = len(list(image_dir.glob("img_*.jpg"))) + 1
            cv2.imwrite(str(image_dir / f"img_{nb_files}.jpg"), im0)

