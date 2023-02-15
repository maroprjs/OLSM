import RPi.GPIO as GPIO
from pn532 import *
import socket
import time
from enum import Enum

UDP_IP = "10.200.21.80"
UDP_PORT = 5555
AGV_TYPE = "ELECTRIC" #"HYBRID"
gHostName = socket.gethostname()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
STATE_TRANSITION_INTERVAL = 1.0
TAG_BIT1_PIN = 17
TAG_BIT2_PIN = 27
TAG_BIT3_PIN = 22
NFC_READER_SENSED_PIN = 3
FLASHLIGHT_PIN = 25
LITTLE_AGV_ATTACHED_PIN = 2 

#fuel tag 21: 48b99f2656081
#fuel tag 22: 4d89bf2656080
#fuel tag 23: 49b9af2656080
#fuel tag 24: 43c89f2656081

#electro tag 25: 41f82f2656081
#electro tag 26: 4808af2656080
#electro tag 27: 4b876f2656080 
#electro tag 28: 46071f2656081
PART_TYPES = {
  "48b99f2656081": "FUEL",
  "4d89bf2656080": "FUEL",
  "49b9af2656080": "FUEL",
  "43c89f2656081": "FUEL",
  "41f82f2656081": "ELECTRO",
  "4808af2656080": "ELECTRO",
  "4b876f2656080": "ELECTRO",
  "46071f2656081": "ELECTRO",
  "00000000":"FREE"
}

GPIO.setmode(GPIO.BCM)
GPIO.setup(TAG_BIT1_PIN, GPIO.OUT) #8101010 -> 8212121 -> 9323232 ...->...8878787
GPIO.setup(TAG_BIT2_PIN, GPIO.OUT)
GPIO.setup(TAG_BIT3_PIN, GPIO.OUT)
GPIO.setup(NFC_READER_SENSED_PIN, GPIO.IN)
GPIO.setup(FLASHLIGHT_PIN, GPIO.OUT)
GPIO.setup(LITTLE_AGV_ATTACHED_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#These are aligned with emulated tags from arduino on AGV part:
class Location(str, Enum): 
    FREE = '00000000'
    station1 = '4e189f2656080'
    station2 = '48f7df2656081'
    station3 = '4547cf2656081'
    station4 = '46195f2656081'
    station5 = '4ff95f2656080'

class AgvState(str, Enum):
    #FREE = '00000000'
    UNEQUIPPED_ELECTRIC = '8101010'
    UNEQUIPPED_HYBRID = '8212121'
    EQUIPPED_ELECTRIC_PART1 = '8323232'
    EQUIPPED_ELECTRIC_PART2 = '8434343'
    #EQUIPPED_ELECTRIC_FULL = '-------' 
    EQUIPPED_HYBRID_FUEL = '8656565'
    EQUIPPED_HYBRID_ELECTRIC = '8767676'
    EQUIPPED_HYBRID_FULL = '8545454'
    WRONG_PART = '88787878'



def get_uid_string(uid):
    uid_str = ''
    for i in uid:
        hex_str = str(hex(i))
        uid_str = uid_str + hex_str[2:]
    return uid_str

def getAgvState(nfc_tag):
    stationState = '' 
    for data in StationState:
        if data.value == nfc_tag:
            stationState = data.name
    return stationState

def getAgvLocation(nfc_tag):
    location = '' 
    for data in Location:
        if data.value == nfc_tag:
            location = data.name
    return location

def publish_U_ELECTRIC(): #sends tag 8101010
   GPIO.output(TAG_BIT1_PIN, False) 
   GPIO.output(TAG_BIT2_PIN, False) 
   GPIO.output(TAG_BIT3_PIN, False)
   gAgvState = AgvState.UNEQUIPPED_ELECTRIC 

def publish_U_HYBRID(): #sends tag 8212121
   GPIO.output(TAG_BIT1_PIN, True) 
   GPIO.output(TAG_BIT2_PIN, False) 
   GPIO.output(TAG_BIT3_PIN, False)
   gAgvState = AgvState.UNEQUIPPED_HYBRID 

def publish_E_ELECTRIC_P1(): #sends tag 8323232
   GPIO.output(TAG_BIT1_PIN, False) 
   GPIO.output(TAG_BIT2_PIN, True) 
   GPIO.output(TAG_BIT3_PIN, False)
   gAgvState = AgvState.EQUIPPED_ELECTRIC_PART1

def publish_E_ELECTRIC_P2(): #sends tag 8434343
   GPIO.output(TAG_BIT1_PIN, True) 
   GPIO.output(TAG_BIT2_PIN, True) 
   GPIO.output(TAG_BIT3_PIN, False)
   gAgvState = AgvState.EQUIPPED_ELECTRIC_PART2

EQUIPPED_HYBRID_FUEL = '8656565'
    EQUIPPED_HYBRID_ELECTRIC = '8767676'
    EQUIPPED_HYBRID_FULL = '8545454'
    WRONG_PART = '88787878'


def inform_server(station_tag, agv_state):
   #sock.sendto(bytes(gHostName + "," + getAgvState(nfc_tag) , "utf-8"), (UDP_IP, UDP_PORT))
   #if getAgvLocation(nfc_tag) == Location.FREE :
   #   publishFree()
   msg = getAgvLocation(station_tag) + "," + agvState; #"stationX,<status>"  
   sock.sendto(bytes(msg, "utf-8"), (UDP_IP, UDP_PORT))
   # if getAgvLocation(nfc_tag) == Location.station1 :
   #     msg = inform local server -> load video
   #     send tstaus to station
   #ToDo

def inform_station(tag):
    if PART_TYPES[tag] == "FUEL":
        if AGV_TYPE == "HYBRID":
            if gAgvState == AgvState.UNEQUIPPED_HYBRID:
                gAgvState = AgvState.EQUIPPED_HYBRID_FUEL
            if gAgvState == AgvState.EQUIPPED_HYBRID_FUEL:
                gAgvState = AgvState.WRONG_PART
            if gAgvState == AgvState.EQUIPPED_HYBRID_ELECTRIC:
                gAgvState = AgvState.EQUIPPED_HYBRID_FULL
        if AGV_TYPE == "ELECTRIC":
                gAgvState = AgvState.WRONG_PART

    if PART_TYPES[tag] == "ELECTRIC":
        if AGV_TYPE == "HYBRID":
            if gAgvState == AgvState.UNEQUIPPED_HYBRID:
                gAgvState = AgvState.EQUIPPED_HYBRID_ELECTRIC
            if gAgvState == AgvState.EQUIPPED_HYBRID_FUEL:
                gAgvState = AgvState.EQUIPPED_HYBRID_FULL
            if gAgvState == AgvState.EQUIPPED_HYBRID_ELECTRIC:
                gAgvState = AgvState.WRONG_PART
        if AGV_TYPE == "ELECTRIC":
            if gAgvState == AgvState.UNEQUIPPED_ELECTRIC:
                gAgvState = AgvState.EQUIPPED_ELECTRIC_PART1
            if gAgvState == AgvState.EQUIPPED_ELECTRIC_PART1:
                gAgvState = AgvState.EQUIPPED_ELECTRIC_PART2

    if PART_TYPES[tag] == "FREE":
        if AGV_TYPE == "HYBRID":
            gAgvState = AgvState.UNEQUIPPED_HYBRID
        if AGV_TYPE == "ELECTRIC":
            gAgvState = AgvState.UNEQUIPPED_ELECTRIC


def initializeStationReader():
    try:
       pn532 = PN532_SPI(debug=False, reset=20, cs=4)
       ic, ver, rev, support = pn532.get_firmware_version()
       print('Found Station Reader with firmware version: {0}.{1}'.format(ver, rev))
       pn532.SAM_configuration()
    except Exception as e:
        print(e)
        return None
        pass
    finally:
        pass
        #GPIO.cleanup()
    return pn532

def initializePart1Reader():
    try:
       pn532 = PN532_SPI(debug=False, reset=20, cs=23)
       ic, ver, rev, support = pn532.get_firmware_version()
       print('Found Part1 with firmware version: {0}.{1}'.format(ver, rev))
       pn532.SAM_configuration()
    except Exception as e:
        print(e)
        return None
        pass
    finally:
        #return None
        pass
        #GPIO.cleanup()
    return pn532

def initializePart2Reader():
    try:
       pn532 = PN532_SPI(debug=False, reset=20, cs=24)
       ic, ver, rev, support = pn532.get_firmware_version()
       print('Found Part2 with firmware version: {0}.{1}'.format(ver, rev))
       pn532.SAM_configuration()
    except Exception as e:
        print(e)
        return None
        pass
    finally:
        #return None
        pass
        #GPIO.cleanup()
    return pn532


if __name__ == '__main__':
    #print($HOSTNAME)
    #print(socket.gethostname())
    station = initializeStationReader()
    part1 = initializePart1Reader()
    part2 = initializePart2Reader()
    smallAgvAttached = True
    stationState = StationState.FREE
    timeToCheckStationState = time.perf_counter() + STATE_TRANSITION_INTERVAL
    try:
        print('Waiting for RFID/NFC card...')
        while True:
            if time.perf_counter() >= timeToCheckStationState: #as long as tag is recognized the time check runs ahead
                if stationState != StationState.FREE:
                    stationState = StationState.FREE
                    inform_server("00000000")
            if GPIO.input(LITTLE_AGV_ATTACHED_PIN) == True:
                smallAgvAttached = False
                time.sleep(1)
            if (GPIO.input(LITTLE_AGV_ATTACHED_PIN) == False) and (smallAgvAttached == False): #high jump recognized
                time.sleep(1)
                station = initializeStationReader()
                part1 = initializePart1Reader()
                part2 = initializePart2Reader()
                smallAgvAttached = True
            
            # Check if a card is available to read
            stationTag = station.read_passive_target(timeout=0.1)
            if stationTag is not None:
               #continue
               print('Found station with nfc UID: ', get_uid_string(stationTag))
            
            if smallAgvAttached == True:
               part1Tag = part1.read_passive_target(timeout=0.1)
               if part1Tag is not None:
                  #continue
                  print('Found part1 with nfc UID: ', get_uid_string(part1Tag))

               part2Tag = part2.read_passive_target(timeout=0.1)
               if part2Tag is not None:
                  #continue
                  print('Found part2 with nfc UID: ', get_uid_string(part2Tag))

    except Exception as e:
        print(e)
        inform_server("error: " + str(e))
        pass
        #goto .begin
    finally:
        #GPIO.cleanup()
        pass

