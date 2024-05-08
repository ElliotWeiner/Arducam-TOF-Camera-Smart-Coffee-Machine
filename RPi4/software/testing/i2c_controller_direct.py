# Author: Elliot Weiner
# Date: 04 / 03 / 2024
# Organization: University of Rochester Electrical and Computer Engineering Department
# Description:
#   This code provides a basic way of interfacing with the hardware controller (Arduino Uno).
#   They use smbus to communicate via I2C protocol.
#

# Commands:
# 0 to stop Gantry
# 1 to move Gantry left
# 2 to move Gantry right
# 3 to open solenoid 1
# 4 to open solenoid 2
# 5 to open solenoid 3
# 6 to open solenoid 4
# 7 to turn off all solenoids

import smbus

if __name__ == "__main__":
    motor_address = 0x8

    bus = smbus.SMBus( 1 )

    while True:
        command = int( input( "Enter Command: " ) )
        bus.write_byte( motor_address, command )