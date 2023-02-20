import RPi.GPIO as GPIO
from pn532 import *
import socket
import time
from enum import Enum

UDP_IP = "192.168.243.134"
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
STATION_SPI_CS_PIN = 4
STOCK1_SPI_CS_PIN = 23
STOCK2_SPI_CS_PIN = 24

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
  "00000000":"NONE"
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
    UNDEFINED = '00000000'
    station1 = '4e189f2656080'
    station2 = '48f7df2656081'
    station3 = '4547cf2656081'
    station4 = '46195f2656081'
    station5 = '4ff95f2656080'

class StockState(Enum):
    EMPTY = 1
    OCCUPIED_ELECTRIC = 2
    OCCUPIED_FUEL = 3
    UNKNOWN_PART = 4


class AgvState(str, Enum):
    UNEQUIPPED_ELECTRIC = '8878787'
    UNEQUIPPED_HYBRID = '8767676'
    EQUIPPED_ELECTRIC_PART1 = '8656565'
    EQUIPPED_ELECTRIC_PART2 = '8545454'
    EQUIPPED_HYBRID_PART1 = '8434343'
    EQUIPPED_HYBRID_PART2 = '8323232'
    WRONG_PART = '8212121'
    #placeholder 8101010



def get_uid_string(uid):
    uid_str = ''
    for i in uid:
        hex_str = str(hex(i))
        uid_str = uid_str + hex_str[2:]
    return uid_str

def getAgvLocation(nfc_tag):
    location = '' 
    for data in Location:
        if data.value == nfc_tag:
            location = data.name
    return location

def getAgvState(stock1_tag, stock2_tag ):
    part1_type = PART_TYPES[stock1_tag]
    part2_type = PART_TYPES[stock2_tag]
    agvState = AgvState.UNEQUIPPED_ELECTRIC

    if AGV_TYPE == "ELECTRIC":
        if part1_type == "NONE"and part2_type == "NONE":
            agvState = AgvState.UNEQUIPPED_ELECTRIC
        elif part1_type == "NONE" and part2_type == "ELECTRIC":
            agvState = AgvState.EQUIPPED_ELECTRIC_PART1
        elif part1_type == "ELECTRIC" and part2_type == "NONE":
            agvState = AgvState.EQUIPPED_ELECTRIC_PART1
        elif part1_type == "ELECTRIC" and part2_type == "ELECTRIC":
            agvState = AgvState.EQUIPPED_ELECTRIC_PART2
        else:
            agvState = AgvState.WRONG_PART

    if AGV_TYPE == "HYBRID":
        if part1_type == "NONE"and part2_type == "NONE":
            agvState == AgvState.UNEQUIPPED_HYBRID
        elif part1_type == "NONE" and part2_type == "FUEL":
            agvState = AgvState.EQUIPPED_HYBRID_PART1
        elif part1_type == "FUEL" and part2_type == "NONE":
            agvState = AgvState.EQUIPPED_HYBRID_PART1
        elif part1_type == "ELECTRIC" and part2_type == "HYBRID":
            agvState = AgvState.EQUIPPED_HYBRID_PART2
        elif part1_type == "HYBRID" and part2_type == "ELECTRIC":
            agvState = AgvState.EQUIPPED_HYBRID_PART2           
        else:
            agvState = AgvState.WRONG_PART

    return agvState


def publishNextAgvState( nextState):
    if nextState == AgvState.UNEQUIPPED_ELECTRIC:
        publish_U_ELECTRIC()
    if nextState == AgvState.UNEQUIPPED_HYBRID:
        publish_U_HYBRID()       
    if nextState == AgvState.EQUIPPED_ELECTRIC_PART1:
        publish_E_ELECTRIC_P1()
    if nextState == AgvState.EQUIPPED_ELECTRIC_PART2:
        publish_E_ELECTRIC_P2()       
    if nextState == AgvState.EQUIPPED_HYBRID_PART1:
        publish_E_HYBRID_P1()
    if nextState == AgvState.EQUIPPED_HYBRID_PART1:
        publish_E_HYBRID_P2()


def publish_U_ELECTRIC(): #sends tag 8878787
   GPIO.output(TAG_BIT1_PIN, True) 
   GPIO.output(TAG_BIT2_PIN, True) 
   GPIO.output(TAG_BIT3_PIN, True)
   gAgvState = AgvState.UNEQUIPPED_ELECTRIC 

def publish_U_HYBRID(): #sends tag 8767676
   GPIO.output(TAG_BIT1_PIN, False) 
   GPIO.output(TAG_BIT2_PIN, True) 
   GPIO.output(TAG_BIT3_PIN, True)
   gAgvState = AgvState.UNEQUIPPED_HYBRID 

def publish_E_ELECTRIC_P1(): #sends tag 8656565
   GPIO.output(TAG_BIT1_PIN, True) 
   GPIO.output(TAG_BIT2_PIN, False) 
   GPIO.output(TAG_BIT3_PIN, True)
   gAgvState = AgvState.EQUIPPED_ELECTRIC_PART1

def publish_E_ELECTRIC_P2(): #sends tag 8545454
   GPIO.output(TAG_BIT1_PIN, False) 
   GPIO.output(TAG_BIT2_PIN, False) 
   GPIO.output(TAG_BIT3_PIN, True)
   gAgvState = AgvState.EQUIPPED_ELECTRIC_PART2

def publish_E_HYBRID_P1(): #sends tag 8434343
   GPIO.output(TAG_BIT1_PIN, True) 
   GPIO.output(TAG_BIT2_PIN, True) 
   GPIO.output(TAG_BIT3_PIN, False)
   gAgvState = AgvState.EQUIPPED_HYBRID_PART1

def publish_E_HYBRID_P2(): #sends tag 8323232
   GPIO.output(TAG_BIT1_PIN, False) 
   GPIO.output(TAG_BIT2_PIN, True) 
   GPIO.output(TAG_BIT3_PIN, False)
   gAgvState = AgvState.EQUIPPED_HYBRID_PART2


def inform_server(location, agv_state): #locat server to play appropriate video
   #msg = getAgvLocation(station_tag) + "," + agvState; #"stationX,<status>"  
   msg = location + "," + agvState; #"stationX,<status>"
   sock.sendto(bytes(msg, "utf-8"), (UDP_IP, UDP_PORT))





def initializeStationReader():
    try:
       pn532 = PN532_SPI(debug=False, reset=20, cs=STATION_SPI_CS_PIN)
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

def initializeStock1Reader():
    try:
       pn532 = PN532_SPI(debug=False, reset=20, cs=STOCK1_SPI_CS_PIN)
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

def initializeStock2Reader():
    try:
       pn532 = PN532_SPI(debug=False, reset=20, cs=STOCK2_SPI_CS_PIN)
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
    smallAgvAttached = True
    stock1State = StockState.EMPTY
    stock2State = StockState.EMPTY
    location = Location.UNDEFINED
    stockCount = 0
    station = initializeStationReader()
    stock1 = initializeStock1Reader()
    stock2 = initializeStock2Reader()
    stock1Tag = "00000000"
    stock2Tag = "00000000"
    #print('Waiting for RFID/NFC cards...')
    agvState = AgvState.UNEQUIPPED_ELECTRIC
    idleState = AgvState.UNEQUIPPED_ELECTRIC
    publishNextAgvState(agvState)
    if AGV_TYPE == "HYBRID":
        agvState = AgvState.UNEQUIPPED_HYBRID
        idleState = AgvState.UNEQUIPPED_HYBRID
    timeToCheckAgvState = time.perf_counter() + STATE_TRANSITION_INTERVAL
    try:
        while True:
            if time.perf_counter() >= timeToCheckAgvState: #as long as tag is present the time check runs ahead and condition not reached
                if location != Location.UNDEFINED: #this just to know when to stop playing local
                    location = Location.UNDEFINED
                    inform_server("00000000")
            if GPIO.input(LITTLE_AGV_ATTACHED_PIN) == True:
                smallAgvAttached = False
                time.sleep(1)
            if (GPIO.input(LITTLE_AGV_ATTACHED_PIN) == False) and (smallAgvAttached == False): #high jump recognized
                time.sleep(1)
                station = initializeStationReader()
                stock1 = initializeStock1Reader()
                stock2 = initializeStock2Reader()
                smallAgvAttached = True
                print('Waiting for RFID/NFC card...')
            
            # Check if a card is available to read
            if station is not None:
               stationTag = station.read_passive_target(timeout=0.1)
               if stationTag is not None:
                  #continue
                  timeToCheckStationState = time.perf_counter() + STATE_TRANSITION_INTERVAL
                  print('Found station with nfc UID: ', get_uid_string(stationTag))
                  if (location != getAgvLocation(stationTag)):
                     location = getAgvLocation(stationTag)
                     inform_server(location, agvState) #to local server TODO            
            if smallAgvAttached == True:
                if (stock1 is not None) and (stock2 is not None): #NFC reader present
                    stock1Tag = stock1.read_passive_target(timeout=0.1)
                    stock2Tag = stock2.read_passive_target(timeout=0.1)
                    if stock1Tag is None:
                        stock1Tag = "00000000"
                    else: 
                        print('Found stock1 with nfc UID: ', get_uid_string(stock1Tag))
                    if stock2Tag is None:
                        stock2Tag = "00000000"
                    else:
                        print('Found stock2 with nfc UID: ', get_uid_string(stock2Tag))

                    if agvState != getAgvState(stock1Tag, stock2Tag):
                        publishNextAgvState( agvState)
                        inform_server(location, agvState) #localServer

                

    except Exception as e:
        print(e)
        #inform_server("error: " + str(e)) #doesn't make sense here
        pass
        #goto .begin
    finally:
        #GPIO.cleanup()
        pass

