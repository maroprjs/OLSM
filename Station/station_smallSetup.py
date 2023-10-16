import RPi.GPIO as GPIO
from pn532 import *
import socket
import time
from enum import Enum
import socketio
import threading

MAIN_GUI_IP = "10.200.20.57" #in order to get its
MAIN_GUI_IO_SOCKET = 80 #in order to get its role
UDP_IP = "10.200.20.57"
UDP_PORT = 5555
gHostName = socket.gethostname() #not used for small setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
STATE_TRANSITION_INTERVAL = 1.5
MIN_NO_OF_SAME_TAGE_BEFORE_TRANSITION = 5
gStationRole = "NONE" #*1) this is for the smal setup; station1 original role is queue
                                                       #station2 original role is assembly
                                                       #station3 original role is cabling
                                                       #station4 original role is programming
                                                       #station5 original role is inspection
                       #but now each station has to be ble for all roles assigned
gStationRoleDict = { #must be same as streamdeck
  "QUEUE":"station1",
  "ASSEMBLY":"station2",
  "CABLING":"station3",
  "PROGRAMMING":"station4", 
  "INSPECTION":"station5"
}

#These are aligned with emulated tags from arduino on AGV part to play the right video:
class StationState(str, Enum): 
    FREE = '00000000'
    UNEQUIPPED_ELECTRIC = '8878787'
    UNEQUIPPED_HYBRID = '8767676'
    EQUIPPED_ELECTRIC_PART1 = '8656565'
    EQUIPPED_ELECTRIC_PART2 = '8545454' #full
    EQUIPPED_HYBRID_PART1 = '8434343'
    EQUIPPED_HYBRID_PART2 = '8323232' #full
    WRONG_PART = '8212121'
    TEST_1 = '8ad1aae'
    TEST_2 = 'f82684d'

def get_uid_string(uid):
    uid_str = ''
    for i in uid:
        hex_str = str(hex(i))
        uid_str = uid_str + hex_str[2:]
    return uid_str

def getStationState(nfc_tag):
    stationState = '' 
    for data in StationState:
        if data.value == nfc_tag:
            stationState = data.name
    return stationState

def inform_server(nfc_tag):
   #global gStationRole
   #global gStationRoleDict
   #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
   #print(getStationState(nfc_tag))
   if gStationRole != "NONE": #TODO: validity check here necessary?
      sock.sendto(bytes(gStationRoleDict[gStationRole] + "," + getStationState(nfc_tag) , "utf-8"), (UDP_IP, UDP_PORT))
   #sock.sendto(bytes(gHostName + "," + getStationState(nfc_tag) , "utf-8"), (UDP_IP, UDP_PORT))
   #sock.close()
   #sock.shutdown(socket.SHUT_RDWR)

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

#@sio.event
#def message(data):
#    print('message received with ', data)    
#    #sio.emit('my response', {'response': 'my response'})

@sio.on('station_mapping_info')
def on_message(data): 
    global gStationRole
    print('I received a message!', data.strip())
    msg = [x.strip() for x in data.split(',')]
    addressedStation = msg[0]
    role = msg[1]
    if addressedStation == gHostName: #streamdeck gives role to stations in network, if station name
       print(role)                    #in message equals its hostname it knows it's role from second part of msg
       gStationRole = role
 
@sio.event
def disconnect():
    print('disconnected from server')

def ioSocketMain():
    global sio
    sio.connect('http://' + MAIN_GUI_IP + ':' + str(MAIN_GUI_IO_SOCKET))
    sio.wait()


if __name__ == '__main__':
    #print($HOSTNAME)
    #print(socket.gethostname())
    ioSocketThread = threading.Thread(target=ioSocketMain)
    ioSocketThread.start()
    stationState = StationState.FREE
    tagTransitionCount = 0
    timeToCheckStationState = time.perf_counter() + STATE_TRANSITION_INTERVAL
    try:
        pn532 = PN532_I2C(debug=False, reset=20, req=16)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()
        print('Waiting for RFID/NFC card...')
        while True:
            if time.perf_counter() >= timeToCheckStationState: #as long as tag is recognized the time check runs ahead
                if stationState != StationState.FREE:
                    stationState = StationState.FREE
                    inform_server("00000000")
                    tagTransitionCount = 0
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=1.5)
            #print('.', end="")
            if uid is not None:
                timeToCheckStationState = time.perf_counter() + STATE_TRANSITION_INTERVAL
                uid_as_str = get_uid_string(uid)
                print('Found card with UID:', [hex(i) for i in uid], 'as string: ', uid_as_str)
                if stationState != getStationState(uid_as_str):
                    tagTransitionCount += 1
                    print(tagTransitionCount)
                    if tagTransitionCount >= MIN_NO_OF_SAME_TAGE_BEFORE_TRANSITION:
                        inform_server(uid_as_str)
                        stationState = getStationState(uid_as_str)
                        tagTransitionCount = 0
    except Exception as e:
        print(e)
        inform_server("error: " + str(e))
    finally:
        GPIO.cleanup()

