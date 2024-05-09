# Arducam TOF Camera Smart Coffee Machine



![Picture of Experimental Design](https://github.com/ElliotWeiner/Arducam-TOF-Camera-Smart-Coffee-Machine/blob/main/resources/media/Live_Test.jpeg?raw=true)
 
*Experimental Design*

## Project Summary


This repository contains the source code for an autonomous coffee dispenser, informally named 'SmartSip'. Its intended use is to reduce the workload of baristas by acting as an 'extra hand' that can pour simple drinks with little assistance from a user; due to its widely applicable innovations on previous pouring technologies, it could easily be adapted for a broader scope of commercial implementations. 
 
The machine features a unique set of innovations that make it ideal for high-customer volume environments: automated cup centering under a custom-built nozzle, cup volume estimation, and hands-free drink pouring based on user input proportioning. These expand upon mainstream liquid dispension methods, in which drinks are often proportioned with a static volume or only one liquid is poured (commonly seen in auto-fill implementations). SmartSip accomplishes these tasks by using [Arducam’s Time of Flight Camera (TOF) for Raspberry Pi](https://www.arducam.com/time-of-flight-camera-raspberry-pi/), which allows the machine to detect changes in range with a surprisingly accurate degree of accuracy.


## Hardware

##### Insert Schematic of Circuitry Here
![Circuit Layout](https://github.com/ElliotWeiner/Arducam-TOF-Camera-Smart-Coffee-Machine/blob/main/resources/media/Circuit.jpeg?raw=true)

*Full Circuit Diagram*

#### Microcontrollers
a Raspberry Pi 4 was used as the 'main' node, taking in user input and serving as the central hub of decision making and communications. It used the Ubuntu 20.04 operating system to allow for ROS compatibility in future applications. The presented issues in implementing the Arducam TOF Camera: it was designed with only Raspbian compatibility in mind. For this reason, a Raspberry Pi 3 was configured with the Raspbian OS and TCP communication capibilities to allow for seamless data transfer between the two. An Arduino Uno was selected as a hardware controller due to its simplistic compatibility with physical components (such as limit switches, stepper motors, etc).

#### One Stepper Motor
![Gantry Test](https://github.com/ElliotWeiner/Arducam-TOF-Camera-Smart-Coffee-Machine/blob/main/resources/media/Gantry_Test.gif?raw=true) 

*Gantry System Post-Fabrication Testing*
 
A stepper motor was used for control of a gantry system, shown above. Because of its uniquely high precision, it provided the system with an accurate method for positioning an attached nozzle.
 
#### Two Limit Switches
Limit switches were used in combination with the stepper motor to simplify gantry control. By attaching them to the ends of the track, the motor could be stopped automatically by the controller, which led to additional ‘self-reset’ capabilities.
 
#### Three Solenoid Valves
Solenoids were attached at the halfway point between filled ingredient tanks and the nozzle to implement a simple fluid control system. These allowed for simplistic control of pouring systems, making them ideal for a proof of concept (POC) prototype. The main notable downside of these was the lack of static flow rate: the fluid system was gravity-powered, making the flow rates entirely reliant upon the tanks’ fullness.
 

## Arducam TOF Camera

![TOF Output](https://github.com/ElliotWeiner/Arducam-TOF-Camera-Smart-Coffee-Machine/blob/main/resources/media/TOF_Output.png?raw=true)

*Example Camera Preview*

The Arducam TOF Camera was used to provide inference capability to the machine. By generating depth images (and from that, laser scans), information about the ground height, the position of a given cup’s rims, and general cup measurements can be acquired and processed. The code regarding our implementation of these can be found in the RPi3 folder under camera_node.py, which details our centering algorithms, bearing adjustments, volume calculations, and laser scan generation.

One of the main reasons the TOF camera was chosen to act as our main source of inference was due to its price, making the project more affordable. However, in our testing we discovered that it had several drawbacks that hindered the design - the most notable of these was the inconsistency between laser scans. We found that consistent millimeter precision was nearly impossible to get without an algorithmic solution, and there didn’t seem to be a consistent pattern to the differences. Our original method of volume estimation, in which an estimate was calculated while a drink was being brewed by observing the liquid height and the flow rate, was thus replaced with a cylindrical calculation with minor adjustments in the absence of robust precision. Additionally, a substantial error was observed in detecting rim heights above 10 centimeters due to the sheer proximity of the sensor to specified points. This was able to be approximated with the function $0.005 *(x-10)^{1.8}$ $while$  $x > 10$ where x was measured in meters, allowing for a repeatably accurate estimation of volume.





## Communication Protocols

### TCP

Transmission Control Protocol (TCP) was used to instantiate basic communication between the Raspberry Pi 3 and 4. The python [‘Socket’ Library](https://www.geeksforgeeks.org/socket-programming-python/) made this relatively simple, as seen in the algorithmic implementations found in RPi3 and RPi4. The prior has this code in the camera_node.py file (client), while the latter has it both in centering.py (server) and a file named set_static_eth0. This file must be moved to the /etc/network/interfaces.d folder to allow for static eth0 initialization on bootup (note: this action will disable wireless connection on the device until it is removed).

### I2C

Inter-Integrated Circuit (I2C) communication was used to connect the RPi4 (master node) with the Arduino Uno hardware controller (slave node). Through this connection, commands could be sent regarding solenoid and stepper motor control. It was implemented primarily through the use of the python [SMBus Library](https://pypi.org/project/smbus/) and the Arduino IDE [Wire.h Class](https://www.arduino.cc/reference/en/language/functions/communication/wire/)
Limit switch data was dealt with directly by the hardware controller. The code for this can be found in the RPi4 centering.py file, along with in the Arduino Uno controller.ino file.








