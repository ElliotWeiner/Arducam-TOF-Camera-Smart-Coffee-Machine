# Author: Elliot Weiner
# Date: 04 / 03 / 2024
# Organization: University of Rochester Electrical and Computer Engineering Department
# Description:
#   This code is meant to provide basic depth-image processing functions for use in volume estimation 
#   of cups. It is intended for use with Arducam's TOF camera. Additional code is implemented for TCP 
#   communication with a 'Master' node which handles a GUI, backend control and I2C communication with 
#   a hardware controller (Arduino Uno).
#


import ArducamDepthCamera as ac
import numpy as np
import math
import socket

# alert 'Master' node when a cup is centered under TOF camera
def center(s, cam):
    centering_threshold = 12
    gnd = 0
    
    while True:
        # get laserscan
        laserScan = get_scan(cam)
        laserScan_cpy = laserScan.copy()
        
        # get ground height
        gnd = np.amax(laserScan)
        gnd = get_height(laserScan, gnd, np.where(laserScan == gnd)[0][0])
        
        # get rims
        val_1, val_2, idx_1, idx_2 = get_rim(laserScan, 15)
        
        # printing
        string = "gnd: " + str(gnd) + "  " + str(abs(int((idx_1 + idx_2)/2))) + " vs " + str(int(len(laserScan)/2)) 
        string += " : " + "{:.2}".format(val_1) + " - {:.2}".format(val_2)
        print(string)


        # check to see if there are two valid rims 
        if val_1 - gnd < -0.06 and val_2 - gnd < -0.06:
            print("cup present")
            
            avg_pixel = abs(int((idx_1 + idx_2) / 2))
            cen_pixel = int(len(laserScan) / 2)
            # check to see if centered
            if abs(avg_pixel - cen_pixel) < centering_threshold:
                
                # additional printing for verbosity
                print("Centered!")
                print(avg_pixel)
                print(cen_pixel)
                print(str(val_1) + " " + str(idx_1))
                print(str(val_2) + " " + str(idx_2))
                print(gnd)

                ret = '1'
                print("sending centered code!")
                s.send(ret.encode())
                return
            
            # if not centered
            else:
                ret = '0'
                s.send(ret.encode())
                
# make a volume estimate of a cup based on laserScan
def volume_estimate(s, cam):
    # get scan
    laserScan = get_scan(cam)
    laserScan_cpy = laserScan.copy()
    
    # get rim
    val_1, val_2, idx_1, idx_2 = get_rim(laserScan, 5)
    
    
    # ground calculation
    gnd = get_height(laserScan_cpy, laserScan_cpy[idx_1 - 5], idx_1 - 5) + get_height(laserScan_cpy, laserScan_cpy[idx_2 + 5], idx_2 + 5)
    gnd = gnd / 2
    
    # get center
    centers = np.zeros(20)
    center_idx = int(len(laserScan_cpy)/2)
    for i in range(center_idx - 10, center_idx + 10):
        centers[i - (center_idx - 10)] = gnd - get_height(laserScan_cpy, laserScan_cpy[i], i)
    center = np.max(centers)

    # pick smaller rim as rim height
    rim = 0
    if val_1 < val_2:
        rim = gnd - get_height(laserScan_cpy, val_1, idx_1)
        print('\r' + "gnd - " + str(gnd) + " | rim and height --> [" + "{:.3}".format(gnd - val_1) + ' ' + "{:.3}".format(rim) + "]  : center --> [" + "{:.3}".format(center) + "]     ")
    else:
        rim = gnd - get_height(laserScan_cpy, val_2, idx_2)
        print('\r' + "gnd - " + str(gnd) + " | rim and height --> [" + "{:.3}".format(gnd - val_2) + ' ' + "{:.3}".format(rim) + "]  : center --> [" + "{:.3}".format(center) + "]     ")

    # calculate approximate volume
    h = (rim - center) * 0.9 # <=== experimental multiplier
    radius = get_radius(laserScan, val_1, val_2, idx_1, idx_2) * 0.78 # <=== experimental multiplier
    print("height: " + str(h))
    print("radius: " + str(radius))

    volume = math.pi * radius**2 * h * 0.745 * 33814.023 # <==== experimental multiplier and convert to oz from square meters
    print("volume: " + str(volume) + " - shape-adjusted volume: " + str(volume * 0.85))
    
    # make shape and error adjustments to volume estimation
    volume = volume * 0.85
    if volume > 10:
        volume = volume - 0.05*(volume - 10)**1.8

    volume = volume * 0.9
    print("error adjusted volume: " + str(volume))
    
    return volume
        
# get laserScan
def get_scan(cam):
    while(1):
        # get frame
        frame = cam.requestFrame(200)
        depth = frame.getDepthData()
        size = depth.shape
        
        # derive laserScan across center row (120 pixels across)
        laserScan = depth[int(size[0]/2),:]
        
        cam.releaseFrame(frame)
        
        # rejection sampling for outlier values ( in our case, values greater than 0.5 meters indicate 'bad' data)
        if not np.any(laserScan > 0.5):
            return laserScan

# get indicies and values of rim of a cup
def get_rim(laserScan, rad):
    # find first rim
    val_1 = np.amin(laserScan)
    idx_1 =  np.where(laserScan == val_1)[0][0]
    
    # ignore radius of pixels around rim
    for i in range(idx_1 - rad, idx_1 + rad):
        try:
            laserScan[i] = 2;
        except:
            continue
            
    # find second rim
    val_2 = np.amin(laserScan)
    idx_2 = np.where(laserScan == val_2)[0][0]
    return val_1, val_2, idx_1, idx_2

# get the height (z distance from camera plane) of a specified point
def get_height(laserScan, value, idx):
    # calculate theta
    center_offset = abs(len(laserScan)/2 - idx)
    theta = math.atan(center_offset / 225.69) #  derived from given image dimensions (240 x 180) and 70 diagonal degree view

    # height
    height  = value * math.cos(theta)

    return height

# get the radius of a cup, specified by two rims (assumes rims indicate actual diameter)
def get_radius(laserScan, val1, val2, idx1, idx2):
    # calculate thetas
    offset1 = abs(len(laserScan)/2 - idx1)
    offset2 = abs(len(laserScan)/2 - idx2)
    theta1 = math.atan(offset1 / 225.69)
    theta2 = math.atan(offset2 / 225.69)
    
    # diameter
    diameter = val1 * math.sin(theta1) + val2 * math.sin(theta2)

    return diameter / 2

# init TCP communication and Arducam TOF camera
def init():
    # init socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 9009
    while 1:
        try:
            s.connect(('169.254.12.13', port))
            break
        except:
            continue
    
    # init ToF camera in 2 meter mode
    cam = ac.ArducamCamera()
    if cam.open(ac.TOFConnect.CSI, 0) != 0:
        print("Failed to init")
    if cam.start(ac.TOFOutput.DEPTH) != 0:
        print("Failed to start")

    cam.setControl(ac.TOFControl.RANG, 2)
    
    return s, cam


if __name__ == "__main__":
    # init TCP commuication and TOF camera
    s, cam = init()

    while(1):
        # wait for start code
        print(s.recv(1024).decode())
        
        # center
        center(s, cam)
        
        # get volume estimate and send
        volume = volume_estimate(s, cam)
        ret = str(volume)
        s.send(ret.encode())
        
        # wait for pour code
        print(s.recv(1024).decode())

    s.close()