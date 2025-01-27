from __future__ import print_function
import matplotlib.pyplot as plt
from builtins import chr
from builtins import str
from builtins import range
import sys
import time
import random
import logging
from datetime import datetime
import threading
from netifaces import interfaces, ifaddresses, AF_INET
import RPi.GPIO as GPIO
from socket import *

GPIO.setwarnings(False)
VERSIONNUMBER = 7
# hey
LIGHT_UPDATE_PACKET = 0
RESET_SWARM_PACKET = 1
CHANGE_TEST_PACKET = 2  # Not Implemented
RESET_ME_PACKET = 3
DEFINE_SERVER_LOGGER_PACKET = 4
LOG_TO_SERVER_PACKET = 5
MASTER_CHANGE_PACKET = 6
BLINK_BRIGHT_LED = 7
MYPORT = 2910
SWARMSIZE = 6
countgraph = [0, 0, 0, 0, 0, 0]
# ax1, ax2 = None, None
loggraph = [0, 0, 0, 0, 0, 0]
# left = [0,1, 2]
tick_label = ["one", "two", "three"]
time_values = []
mastervalue_values = []
masterID_values = []
prev_masterID = None
line_segments = []
plt.ion()

BUTTON = 20
YELLOW_LED_PIN = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)

timeslice = []
timeslice_temp = []
avg_vals=[]
start_time = 0
curr_time = 0


def SendDEFINE_SERVER_LOGGER_PACKET(s):
    print("DEFINE_SERVER_LOGGER_PACKET Sent")
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    # get IP address
    for ifaceName in interfaces():
        addresses = [
            i["addr"]
            for i in ifaddresses(ifaceName).setdefault(
                AF_INET, [{"addr": "No IP addr"}]
            )
        ]
        print("%s: %s" % (ifaceName, ", ".join(addresses)))

    # last interface (wlan0) grabbed
    print(addresses)
    myIP = addresses[0].split(".")
    print(myIP)
    data = ["" for i in range(14)]

    data[0] = int("F0", 16).to_bytes(1, "little")
    data[1] = int(DEFINE_SERVER_LOGGER_PACKET).to_bytes(1, "little")
    data[2] = int("FF", 16).to_bytes(
        1, "little"
    )  # swarm id (FF means not part of swarm)
    data[3] = int(VERSIONNUMBER).to_bytes(1, "little")
    data[4] = int(myIP[0]).to_bytes(1, "little")  # 1 octet of ip
    data[5] = int(myIP[1]).to_bytes(1, "little")  # 2 octet of ip
    data[6] = int(myIP[2]).to_bytes(1, "little")  # 3 octet of ip
    data[7] = int(myIP[3]).to_bytes(1, "little")  # 4 octet of ip
    data[8] = int(0x00).to_bytes(1, "little")
    data[9] = int(0x00).to_bytes(1, "little")
    data[10] = int(0x00).to_bytes(1, "little")
    data[11] = int(0x00).to_bytes(1, "little")
    data[12] = int(0x00).to_bytes(1, "little")
    data[13] = int(0x0F).to_bytes(1, "little")
    mymessage = "".encode()
    s.sendto(mymessage.join(data), ("<broadcast>".encode(), MYPORT))


def SendRESET_SWARM_PACKET(s):
    print("RESET_SWARM_PACKET Sent")
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    data = ["" for i in range(14)]

    data[0] = int("F0", 16).to_bytes(1, "little")

    data[1] = int(RESET_SWARM_PACKET).to_bytes(1, "little")
    data[2] = int("FF", 16).to_bytes(
        1, "little"
    )  # swarm id (FF means not part of swarm)
    data[3] = int(VERSIONNUMBER).to_bytes(1, "little")
    data[4] = int(0x00).to_bytes(1, "little")
    data[5] = int(0x00).to_bytes(1, "little")
    data[6] = int(0x00).to_bytes(1, "little")
    data[7] = int(0x00).to_bytes(1, "little")
    data[8] = int(0x00).to_bytes(1, "little")
    data[9] = int(0x00).to_bytes(1, "little")
    data[10] = int(0x00).to_bytes(1, "little")
    data[11] = int(0x00).to_bytes(1, "little")
    data[12] = int(0x00).to_bytes(1, "little")
    data[13] = int(0x0F).to_bytes(1, "little")

    mymessage = "".encode()
    s.sendto(mymessage.join(data), ("<broadcast>".encode(), MYPORT))


def SendRESET_ME_PACKET(s, swarmID):
    print("RESET_ME_PACKET Sent")
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    data = ["" for i in range(14)]

    data[0] = int("F0", 16).to_bytes(1, "little")

    data[1] = int(RESET_ME_PACKET).to_bytes(1, "little")
    data[2] = int(swarmStatus[swarmID][5]).to_bytes(1, "little")
    data[3] = int(VERSIONNUMBER).to_bytes(1, "little")
    data[4] = int(0x00).to_bytes(1, "little")
    data[5] = int(0x00).to_bytes(1, "little")
    data[6] = int(0x00).to_bytes(1, "little")
    data[7] = int(0x00).to_bytes(1, "little")
    data[8] = int(0x00).to_bytes(1, "little")
    data[9] = int(0x00).to_bytes(1, "little")
    data[10] = int(0x00).to_bytes(1, "little")
    data[11] = int(0x00).to_bytes(1, "little")
    data[12] = int(0x00).to_bytes(1, "little")
    data[13] = int(0x0F).to_bytes(1, "little")

    mymessage = "".encode()
    s.sendto(mymessage.join(data), ("<broadcast>".encode(), MYPORT))


def SendCHANGE_TEST_PACKET(s, swarmID):
    print("RESET_ME_PACKET Sent")
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    data = ["" for i in range(14)]

    data[0] = int("F0", 16).to_bytes(1, "little")

    data[1] = int(RESET_ME_PACKET).to_bytes(1, "little")
    data[2] = int(swarmStatus[swarmID][5]).to_bytes(1, "little")

    data[3] = int(VERSIONNUMBER).to_bytes(1, "little")
    data[4] = int(0x00).to_bytes(1, "little")
    data[5] = int(0x00).to_bytes(1, "little")
    data[6] = int(0x00).to_bytes(1, "little")
    data[7] = int(0x00).to_bytes(1, "little")
    data[8] = int(0x00).to_bytes(1, "little")
    data[9] = int(0x00).to_bytes(1, "little")
    data[10] = int(0x00).to_bytes(1, "little")
    data[11] = int(0x00).to_bytes(1, "little")
    data[12] = int(0x00).to_bytes(1, "little")
    data[13] = int(0x0F).to_bytes(1, "little")

    mymessage = "".encode()
    s.sendto(mymessage.join(data), ("<broadcast>".encode(), MYPORT))


def SendBLINK_BRIGHT_LED(s, swarmID, seconds):
    print("BLINK_BRIGHT_LED Sent")
    print("swarmStatus=", swarmStatus)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    data = ["" for i in range(0, 14)]

    data[0] = int("F0", 16).to_bytes(1, "little")

    data[1] = int(BLINK_BRIGHT_LED).to_bytes(1, "little")
    print("swarmStatus[swarmID][5]", swarmStatus[swarmID][5])

    data[2] = int(swarmStatus[swarmID][5]).to_bytes(1, "little")
    data[3] = int(VERSIONNUMBER).to_bytes(1, "little")
    if seconds > 12.6:
        seconds = 12.6
    data[4] = int(seconds * 10).to_bytes(1, "little")
    data[5] = int(0x00).to_bytes(1, "little")
    data[6] = int(0x00).to_bytes(1, "little")
    data[7] = int(0x00).to_bytes(1, "little")
    data[8] = int(0x00).to_bytes(1, "little")
    data[9] = int(0x00).to_bytes(1, "little")
    data[10] = int(0x00).to_bytes(1, "little")
    data[11] = int(0x00).to_bytes(1, "little")
    data[12] = int(0x00).to_bytes(1, "little")
    data[13] = int(0x0F).to_bytes(1, "little")

    mymessage = "".encode()
    s.sendto(mymessage.join(data), ("<broadcast>".encode(), MYPORT))


SDI = 24
RCLK = 23
SRCLK = 18
placePin = (10, 22, 27, 17)
number = (0xC0, 0xF9, 0xA4, 0xB0, 0x99, 0x92, 0x82, 0xF8, 0x80, 0x90)
SDI_led = 26
RCLK_led = 19
SRCLK_led = 13
code_H = [0x80, 0xC0, 0xE0, 0xF0, 0xF8, 0xFC, 0xFE, 0xFF]
code_L = [0x7F, 0xBF, 0xDF, 0xEF, 0xF7, 0xFB, 0xFD, 0xFE]

led_counter = 0


def displayLEDmatrix():
    time.sleep(1)
    if avg_vals:
        print("\n\n\n\n WE ARE HJERE \n\n\n\n")
        global led_counter, master_average, count
        hc595_shift(code_L[led_counter % 8], SDI_led, SRCLK_led, RCLK_led)
        temp_avg_1 = sum(avg_vals)/len(avg_vals)
        hc595_shift(code_H[int(temp_avg_1) // 145], SDI_led, SRCLK_led, RCLK_led)
        led_counter += 1
        master_average = 0
        count = 0
    # clearDisplay(SDI_led, SRCLK_led, RCLK_led)


def clearDisplay(sdi, srclk, rclk):
    for _ in range(8):
        GPIO.output(sdi, 1)
        GPIO.output(srclk, GPIO.HIGH)
        GPIO.output(srclk, GPIO.LOW)
    GPIO.output(rclk, GPIO.HIGH)
    GPIO.output(rclk, GPIO.LOW)


def hc595_shift(data, sdi, srclk, rclk):
    for i in range(8):
        GPIO.output(sdi, 0x80 & (data << i))
        GPIO.output(srclk, GPIO.HIGH)
        GPIO.output(srclk, GPIO.LOW)
    GPIO.output(rclk, GPIO.HIGH)
    GPIO.output(rclk, GPIO.LOW)


def pickDigit(digit):
    for i in placePin:
        GPIO.output(i, GPIO.LOW)
    GPIO.output(placePin[digit], GPIO.HIGH)


def display7segment():
    global master_id
    for _ in range(5 * 10):
        pickDigit(0)
        hc595_shift(number[master_id % 10], SDI, SRCLK, RCLK)
        time.sleep(0.01)
        pickDigit(1)
        hc595_shift(number[master_id % 100 // 10], SDI, SRCLK, RCLK)
        time.sleep(0.01)
        pickDigit(2)
        hc595_shift(number[master_id % 1000 // 100], SDI, SRCLK, RCLK)
        time.sleep(0.01)
        pickDigit(3)
        hc595_shift(number[master_id % 10000 // 1000], SDI, SRCLK, RCLK)
        time.sleep(0.01)
    clearDisplay(SDI, SRCLK, RCLK)


def setup_7segment_and_led():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SDI, GPIO.OUT)
    GPIO.setup(RCLK, GPIO.OUT)
    GPIO.setup(SRCLK, GPIO.OUT)
    GPIO.setup(SDI_led, GPIO.OUT)
    GPIO.setup(SRCLK_led, GPIO.OUT)
    GPIO.setup(RCLK_led, GPIO.OUT)
    GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
    for i in placePin:
        GPIO.setup(i, GPIO.OUT)


master_id = 0
master_value = 0
count = 0
master_average = 0


def parseLogPacket(message):
    global count, master_average, master_id, master_value
    incomingSwarmID = setAndReturnSwarmID((message[2]))
    print("Log From SwarmID:", (message[2]))
    logString = ""
    for i in range(0, (message[3])):
        logString = logString + chr((message[i + 5]))

    swarmList = logString.split("|")
    swarmElement0 = swarmList[0].split(",")
    master_value = swarmElement0[3]
    master_id = int(message[2])
    thread_names = [t.name for t in threading.enumerate()]
    if "Display7" not in thread_names:
        display_segment = threading.Thread(target=display7segment, name="Display7")
        display_segment.start()
    master_average = (count * master_average + int(master_value)) / (count + 1)
    count += 1
    if "DisplayLED" not in thread_names:
        display_led = threading.Thread(target=displayLEDmatrix, name="DisplayLED")
        display_led.start()

    return logString


def setAndReturnSwarmID(incomingID):
    for i in range(0, SWARMSIZE):
        if swarmStatus[i][5] == incomingID:
            return i
        else:
            if swarmStatus[i][5] == 0:  # not in the system, so put it in
                swarmStatus[i][5] = incomingID
                print("incomingID %d " % incomingID)
                print("assigned #%d" % i)
                return i

    # if we get here, then we have a new swarm member.
    # Delete the oldest swarm member and add the new one in
    # (this will probably be the one that dropped out)

    oldTime = time.time()
    oldSwarmID = 0
    for i in range(0, SWARMSIZE):
        if oldTime > swarmStatus[i][1]:
            oldTime = swarmStatus[i][1]
            oldSwarmID = i

    # remove the old one and put this one in....
    swarmStatus[oldSwarmID][5] = incomingID
    # the rest will be filled in by Light Packet Receive
    # print("oldSwarmID %i" % oldSwarmID)

    return oldSwarmID


# set up sockets for UDP

s = socket(AF_INET, SOCK_DGRAM)
host = "localhost"
s.bind(("", MYPORT))

print("--------------")
print("LightSwarm Logger")
print("Version ", VERSIONNUMBER)
print("--------------")


# first send out DEFINE_SERVER_LOGGER_PACKET to tell swarm where to send logging information

SendDEFINE_SERVER_LOGGER_PACKET(s)
time.sleep(3)
SendDEFINE_SERVER_LOGGER_PACKET(s)


# swarmStatus
swarmStatus = [[0 for x in range(6)] for x in range(SWARMSIZE)]

# 6 items per swarm item

# 0 - NP  Not present, P = present, TO = time out
# 1 - timestamp of last LIGHT_UPDATE_PACKET received
# 2 - Master or slave status   M S
# 3 - Current Test Item - 0 - CC 1 - Lux 2 - Red 3 - Green  4 - Blue
# 4 - Current Test Direction  0 >=   1 <=
# 5 - IP Address of Swarm


for i in range(0, SWARMSIZE):
    swarmStatus[i][0] = "NP"
    swarmStatus[i][5] = 0


# 300 seconds round
seconds_300_round = time.time() + 300.0

# 120 seconds round
seconds_120_round = time.time() + 120.0


def logging_function(incomingSwarmID):
    global loggraph
    swarmList = logString.split("|")
    loggraph[incomingSwarmID] += 1
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_log_filename = f"logfile_{current_time}.log"

    print(f"Saving data since last button press to {new_log_filename}")
    logging.basicConfig(
        filename=new_log_filename,
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
    )
    logging.info(
        f"Master Device: {incomingSwarmID} | Duration: {loggraph[incomingSwarmID]} seconds"
    )
    logging.info(f"Raw Data: {swarmList}")

def load_vals(s_t):
    global timeslice, timeslice_temp
    if int(time.time()-s_t) % 4 == 0:
        if len(timeslice) > 8:
            timeslice=timeslice[-7:]
        timeslice.append(timeslice_temp)
        print(timeslice_temp)
        timeslice_temp=[]
        avg_vals=[]
        for i in timeslice:
            avg_vals.append(sum(i)/len(i))
        print("Avg Vals : {}".format(avg_vals))
        time.sleep(1)
    else:
        swarmList = logString.split("|")
        print("swarmlist=", swarmList)
        swarmElement0 = swarmList[0].split(",")
        mastervalue = swarmElement0[3]
        timeslice_temp.append(int(master_value))


def button_pressed(channel):
    global countgraph

    print("Button has been pressed -------------------\n")

    # Close the current log file
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        handler.close()

    # Send RESET_SWARM_PACKET
    SendRESET_SWARM_PACKET(s)

    # Toggle the yellow LED for 3 seconds
    GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(YELLOW_LED_PIN, GPIO.LOW)

    # Start a new log file
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_log_filename = f"logfile_{current_time}.log"

    # Add a new FileHandler with the updated filename
    file_handler = logging.FileHandler(new_log_filename)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logging.root.addHandler(file_handler)

    # Reset the countgraph or perform any other necessary actions
    countgraph = 0


GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback=button_pressed, bouncetime=300)

try:
    setup_7segment_and_led()
    start_time=time.time()
    while 1:
        if int(time.time()-start_time) % 30 == 0:
            print(timeslice)
            timeslice=timeslice[-8:]
            time.sleep(1)
        d = s.recvfrom(1024)
        message = d[0]
        addr = d[1]
        incomingSwarmID = 0
        if len(message) == 14:
            if message[1] == LIGHT_UPDATE_PACKET:
                incomingSwarmID = setAndReturnSwarmID((message[2]))
                swarmStatus[incomingSwarmID][0] = "P"
                swarmStatus[incomingSwarmID][1] = time.time()

            if (message[1]) == RESET_SWARM_PACKET:
                print("Swarm RESET_SWARM_PACKET Received")
                print("received from addr:", addr)

            if (message[1]) == CHANGE_TEST_PACKET:
                print("Swarm CHANGE_TEST_PACKET Received")
                print("received from addr:", addr)

            if (message[1]) == RESET_ME_PACKET:
                print("Swarm RESET_ME_PACKET Received")
                print("received from addr:", addr)

            if (message[1]) == DEFINE_SERVER_LOGGER_PACKET:
                print("Swarm DEFINE_SERVER_LOGGER_PACKET Received")
                print("received from addr:", addr)

            if (message[1]) == MASTER_CHANGE_PACKET:
                print("Swarm MASTER_CHANGE_PACKET Received")
                print("received from addr:", addr)

        else:
            if (message[1]) == LOG_TO_SERVER_PACKET:
                # print("Swarm LOG_TO_SERVER_PACKET Received")
                incomingSwarmID = setAndReturnSwarmID((message[2]))

                # process the Log Packet
                logString = parseLogPacket(message)
                logging_function(incomingSwarmID)
                load_vals(start_time)

            else:
                print("error message length = ", len(message))

except KeyboardInterrupt:
    print("\nProgram terminatedd by user.")
