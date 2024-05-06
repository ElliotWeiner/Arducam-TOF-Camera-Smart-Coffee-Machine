# Author: Elliot Weiner
# Date: 04 / 03 / 2024
# Organization: University of Rochester Electrical and Computer Engineering Department
# Description:
#   This code serves as the backend control for the entirety of the coffee machine. It interpets camera_node.py's TCP-based messages and makes 
#   decisions on cup centering and pouring. These decisions are then sent via I2C to a hardware controller.
#


import socket
import smbus
import time

# initialize socket communication
def int_com(s):

    # socket setup
    host = '169.254.12.13'
    port = 9009
    s.bind(('', port))

    s.listen( 1 )

# center a given cup
def center(c, bus, address):
    # sync with camera_node.py
    print("connected to by :", addr)
    c.send(b'Ready to make some coffee?')
    
    time.sleep(0.1)

    # start search
    bus.write_byte( address , 2 )
    centered = False;

    while not centered:
        # wait until camera node sends found code 1
        inp = int(c.recv(1024).decode())
        print(inp)

        if inp == 1:
            bus.write_byte( address , 0 )
            print('centered!')
            centered = True

# pour based on volume estimate and given proportions
def pour(vol, bus1, address1, recipe):
    # experimentally calculated flowrates
    flowrates = [0.2, 0.2, 0.2]

    # for each ingredient in recipe, pour
    for i in range(len(recipe)):
        # pour time
        t = vol * recipe[i] / flowrates[i] # oz * % / oz * s = s
        
        string =" pouring ingredient " + str(i) + " for " + str(t) + " seconds."
        print(string)
        
        # pour
        bus1.write_byte(address1, 3+i)
        time.sleep(t)
        bus1.write_byte(address1, 7)

    return

# get a recipe from a txt file
def get_recipe():
    while(1):
        # get text file
        text = open('TS/smartSip/orders.txt', 'r')
        text = text.readlines()

        # convert txt contents to recipe array
        if len(text) > 0:
            recipe = [0.0,0.0,0.0]
            for line in text:
                split = line.split(':')
                
                if split[0] == "Milk":
                    recipe[1] = float(split[1]) / 100
                elif split[0] == "Coffee":
                    recipe[2] = float(split[1]) / 100
                elif split[0] == "Non-Dairy":
                    recipe[0] = float(split[1]) / 100
            return recipe

if __name__ == '__main__':

    # init socket communication
    sock = socket.socket()
    int_com(sock)

    # init bus specs
    address1 = 0x8
    bus1 = smbus.SMBus( 1 )

    # init com bus
    c, addr = sock.accept()

    while(1):
        # get recipe
        recipe = get_recipe()
        print(recipe)

        # center
        center(c, bus1, address1)

        # sync centering_node.py
        time.sleep(1)
        msg = "Pouring"
        c.send(msg.encode())

        
        
        # get volume estimate and pour
        vol = float(c.recv(1024).decode())
        pour(vol, bus1, address1, recipe)
        
        # clear file
        text = open('TS/smartSip/orders.txt', 'w')
        text.close()
        
        # reset nozzle position and break
        print("time to reset")
        bus1.write_byte(address1, 1)
        time.sleep(5)
        

    # close coms
    c.close()
    sock.close()