# Arducam TOF Camera Smart Coffee Machine



![Picture of Experimental Design](https://github.com/ElliotWeiner/Arducam-TOF-Camera-Smart-Coffee-Machine/blob/main/resources/media/Live_Test.jpeg?raw=true)
 
*Experimental Design*

## Project Summary

This repository contains the source code for an autonomous coffee dispenser, informally named 'SmartSip'. Its intended use is to reduce the workload of baristas by acting as an 'extra hand' that can pour simple drinks with little assistance from a user. Due to its improvements on previous pouring technologies, it could easily be adapted for a broader scope of commercial implementations. 
 
The machine hosts unique features that make it ideal for high-customer volume environments: automated cup centering under a custom-built nozzle, cup volume estimation, and hands-free drink pouring based on user input proportioning. These expand upon mainstream liquid dispensing methods, in which drinks are proportioned with a static volume or only one liquid is poured (commonly seen in auto-fill implementations). SmartSip accomplishes these tasks by using [Arducam’s Time of Flight Camera (TOF) for Raspberry Pi](https://www.arducam.com/time-of-flight-camera-raspberry-pi/), which allows the machine to detect changes in range with a surprising degree of accuracy.


## Hardware

![Circuit Layout](https://github.com/ElliotWeiner/Arducam-TOF-Camera-Smart-Coffee-Machine/blob/main/resources/media/Circuit.jpeg?raw=true)

*Full Circuit Diagram*

#### Microcontrollers
A Raspberry Pi 4 was used as the 'main' node, taking in user input and serving as the central hub of decision-making and communications. It used the Ubuntu 20.04 operating system to allow for ROS compatibility in future applications. However, this presented issues when implemented alongside the Arducam TOF Camera, as it was designed with only Raspbian compatibility in mind. For this reason, a Raspberry Pi 3 was configured with the Raspbian OS and TCP communication capabilities, allowing for seamless data transfer between the two. Additionally, an Arduino Uno was selected as a hardware controller due to its compatibility with physical components (such as limit switches, stepper motors, etc).

#### One Stepper Motor
![Gantry Test](https://github.com/ElliotWeiner/Arducam-TOF-Camera-Smart-Coffee-Machine/blob/main/resources/media/Gantry_Test.gif?raw=true) 

*Gantry System Testing*
 
A stepper motor was used to control the gantry system, which is shown above. Because of its high precision, it provided the system with an accurate method for positioning the attached nozzle.
 
#### Two Limit Switches
Limit switches were used in combination with the stepper motor to simplify gantry control. By attaching them to the ends of the track, the motor could be stopped automatically by the controller, which led to additional ‘self-reset’ capabilities.
 
#### Three Solenoid Valves
In order to implement a simple fluid control system, solenoids were attached at the halfway point between filled ingredient tanks and the nozzle. These allowed for reliable control of pouring systems, making them ideal for a proof of concept (POC) prototype. The main downside of these valves was the lack of static flow rate. Because the fluid system was gravity-powered, the flow rates were entirely reliant upon the tanks’ fullness.
 

## Arducam TOF Camera

![TOF Output](https://github.com/ElliotWeiner/Arducam-TOF-Camera-Smart-Coffee-Machine/blob/main/resources/media/TOF_Output.png?raw=true)

*Example Camera Preview*

The Arducam TOF Camera was used to provide inference capability to the machine. By generating depth images (and from that, laser scans), information about the ground height, the position of a given cup’s rims, and general cup measurements could be acquired and processed. The code for these functions can be found in the RPi3 folder under camera_node.py, which details our centering algorithms, bearing adjustments, volume calculations, and laser scan generation.

One of the main reasons we chose to use the TOF camera was due to its low price, making the project more affordable. However, we discovered that it had several drawbacks — the most notable of these being the inconsistency between laser scans. It was noticed early on in our testing that no two depth frames gave consistent measurements for range values at the same locations. Unfortunately, consistent millimeter precision was nearly impossible without an algorithmic solution, and there didn’t seem to be a consistent pattern to the differences. Because of this imprecision, we replaced the original method of volume estimation, which calculated volume by observing the liquid height and flow rate. In its place, we implemented a cylindrical calculation, which featured minor adjustments tailored to improve precision. Additionally, a substantial error was observed in detecting rim heights above 10 centimeters. This error was due to the proximity of the sensor to certain cup rims, in addition to the sensitivity of lidar technology. To solve this issue, we implemented an error-accommodation function $0.005 *(x-10)^{1.8}$ $while$ $x > 10$ where x was measured in meters, allowing for a repeatedly accurate estimation of volume.

## Communication Protocols

### TCP

Transmission Control Protocol (TCP) was used to instantiate basic communication between the Raspberry Pi 3 and 4. The python [‘Socket’ Library](https://www.geeksforgeeks.org/socket-programming-python/) made this relatively simple, which can be observed in the implementations for RPi3 and RPi4. The RPi3 code can be located in the camera_node.py file (client), while that for the RPi4 is found both in centering.py (server) and an interface configuration file named set_static_eth0. To work correctly, this file must be moved to the /etc/network/interfaces.d folder to allow for static eth0 initialization on bootup (note: this action will disable wireless connection on the device until it is removed).

### I2C

We implemented Inter-Integrated Circuit (I2C) communication to connect the RPi4 (master node) with the Arduino Uno hardware controller (slave node). Through this connection, commands could be sent regarding solenoid and stepper motor control. This setup was facilitated primarily through the use of the python [SMBus Library](https://pypi.org/project/smbus/) and the Arduino IDE [Wire.h Class](https://www.arduino.cc/reference/en/language/functions/communication/wire/)
Limit switch data was dealt with directly by the hardware controller. The code for this can be found in the RPi4 centering.py file and the Arduino Uno controller.ino file.

