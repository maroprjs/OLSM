import RPi.GPIO as GPIO
from pn532 import *
import socket
import time
from enum import Enum

UDP_IP = "10.200.20.57"
UDP_PORT = 5555
gHostName = socket.gethostname()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
STATE_TRANSITION_INTERVAL = 1.5
MIN_NO_OF_SAME_TAGE_BEFORE_TRANSITION = 5


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
   #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
   #print(getStationState(nfc_tag))
   sock.sendto(bytes(gHostName + "," + getStationState(nfc_tag) , "utf-8"), (UDP_IP, UDP_PORT))
   #sock.close()
   #sock.shutdown(socket.SHUT_RDWR)


if __name__ == '__main__':
    #print($HOSTNAME)
    #print(socket.gethostname())
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

