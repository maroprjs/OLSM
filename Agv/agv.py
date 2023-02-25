import RPi.GPIO as GPIO
from pn532 import *
import socket
import time
from enum import Enum
import board
import neopixel
import os

UDP_IP = "127.0.0.1"
UDP_PORT = 5555
AGV_TYPE = "HYBRID"  #"ELECTRIC"
gHostName = socket.gethostname()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
STATE_TRANSITION_INTERVAL = 2.0
MIN_NO_OF_SAME_TAGE_BEFORE_TRANSITION = 1
TAG_BIT1_PIN = 17
TAG_BIT2_PIN = 27
TAG_BIT3_PIN = 22
NFC_READER_SENSED_PIN = 3
FLASHLIGHT_PIN = 25
LITTLE_AGV_ATTACHED_PIN = 2 
STATION_SPI_CS_PIN = 4
STOCK1_SPI_CS_PIN = 23
STOCK2_SPI_CS_PIN = 24
pixel_pin = board.D18


# The number of NeoPixels
num_pixels = 35
# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.8, auto_write=False, pixel_order=ORDER
)

#neopixel
UNDEFINED = "white"
WAITING1 = "blue"
WAITING2 = "green"
PROGRESS = "orange"
TRANSMIT = "violett"
RED = "red"
gFlipFlop = False


###TODO: move these to config!
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
  "41f82f2656081": "ELECTRIC",
  "4808af2656080": "ELECTRIC",
  "4b876f2656080": "ELECTRIC",
  "46071f2656081": "ELECTRIC",
  "00000000":"NONE"
}

#These are aligned with emulated tags from arduino on AGV part:
#should this replace below enumeration?
#Location = {
#    'UNDEFINED':'00000000',
#    'station1':'4e189f2656080',
#    'station2':'48f7df2656081',
#    'station3':'4547cf2656081',
#    'station4':'46195f2656081',
#    'station5':'4ff95f2656080',
#    'station6':'4ae85f2656080' #tag 19 for test
#}

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
    station6 = '4ae85f2656080' #tag 19 for test

#class StockState(Enum): at the moment obsolete
#    EMPTY = 1
#    OCCUPIED_ELECTRIC = 2
#    OCCUPIED_FUEL = 3
#    UNKNOWN_PART = 4


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
    if uid is None:
        return '00000000'
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

def getAgvStateAsString(nfc_tag):
    state = ''
    for data in AgvState:
        if data.value == nfc_tag:
            state = data.name
    return state

def getAgvState(stock1_tag, stock2_tag ):
    part1_type = PART_TYPES[stock1_tag]
    part2_type = PART_TYPES[stock2_tag]
    agvState = AgvState.UNEQUIPPED_ELECTRIC

    if AGV_TYPE == "HYBRID":
        agvState = AgvState.UNEQUIPPED_HYBRID

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
        elif part1_type == "ELECTRIC" and part2_type == "FUEL":
            agvState = AgvState.EQUIPPED_HYBRID_PART2
        elif part1_type == "FUEL" and part2_type == "ELECTRIC":
            agvState = AgvState.EQUIPPED_HYBRID_PART2           
        else:
            agvState = AgvState.WRONG_PART
    return agvState

def publishNextAgvState(nextState):
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
    if nextState == AgvState.WRONG_PART:
        publish_WRONG_PART()

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

def publish_WRONG_PART(): #sends tag 8212121
   GPIO.output(TAG_BIT1_PIN, True)
   GPIO.output(TAG_BIT2_PIN, False)
   GPIO.output(TAG_BIT3_PIN, False)
   gAgvState = AgvState.WRONG_PART

def inform_server(location, agvStateTag): #locat server to play appropriate video
   #msg = getAgvLocation(station_tag) + "," + agvState; #"stationX,<status>"  
   msg = location + "," + getAgvStateAsString(agvState); #"stationX,<status>"
   sock.sendto(bytes(msg, "utf-8"), (UDP_IP, UDP_PORT))

def initializeStationReader():
    try:
       pn532 = PN532_SPI(debug=False, reset=20, cs=STATION_SPI_CS_PIN)
       ic, ver, rev, support = pn532.get_firmware_version()
       print('Found Station Reader with firmware version: {0}.{1}'.format(ver, rev))
       pn532.SAM_configuration()
    except Exception as e:
        print(e)
        #time.sleep(3)
        #initializeStationReader()
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

def setNeopixel(colr):
   global gFlipFlop
   global pixels
   if gFlipFlop == False:
     gFlipFlop = True
     if colr == "white":
        pixels.fill((5, 5, 5))
     if colr == "blue":
        pixels.fill((0, 0, 5))
     if colr == "green":
        pixels.fill((0, 5, 0))
     if colr == "orange":
        pixels.fill((15,5, 0))
     if colr == "violett":
        pixels.fill((17, 2, 40))
     if colr == "red":
        pixels.fill((5, 0, 0))
   else:
        pixels.fill((0, 0, 0))
        gFlipFlop = False
   pixels.show()

def setNeopixelInitOn():
    global pixels
    pixels.fill((25,5,0))
    pixels.show()

def setNeopixelRedOn():
    global pixels
    pixels.fill((10,0,0))
    pixels.show()

def setNeopixelPurpleOn():
    global pixels
    pixels.fill((17,2,40))
    pixels.show()

def setNeopixelGreenOn():
    global pixels
    pixels.fill((0,5,0))
    pixels.show()

def setNeopixelWhiteOn():
    global pixels
    pixels.fill((5,5,5))
    pixels.show()

def setNeopixelOff():
    global pixels
    pixels.fill((0,0,0))
    pixels.show()


if __name__ == '__main__':
    #print($HOSTNAME)
    #print(socket.gethostname())
    smallAgvAttached = False
    #stock1State = StockState.EMPTY
    #stock2State = StockState.EMPTY
    location = Location.UNDEFINED
    #stockCount = 0
    tagTransitionCount = 0
    stationNotDetected = False #nc reader for station id
    setNeopixelInitOn()
    station = initializeStationReader()
    stock1 = initializeStock1Reader()
    stock2 = initializeStock2Reader()
    setNeopixelOff()
    stock1Tag = "00000000"
    stock2Tag = "00000000"
    agvState = AgvState.UNEQUIPPED_ELECTRIC
    publishNextAgvState(agvState)
    if AGV_TYPE == "HYBRID":
        agvState = AgvState.UNEQUIPPED_HYBRID
    GPIO.output(FLASHLIGHT_PIN, False)
    timeToCheckLocState = time.perf_counter() + STATE_TRANSITION_INTERVAL
    timeToCheckAgvState = time.perf_counter() + STATE_TRANSITION_INTERVAL
    timeToSwitchNeopixel = time.perf_counter() +  1.0
    try:
        while True:
            if time.perf_counter() >= timeToCheckLocState: #as long as tag is present the time check runs ahead and condition not reached
                if location != getAgvLocation("00000000"): #this just to know when to stop playing local
                    location = getAgvLocation("00000000")
                    loc_str = getAgvLocation("00000000")
                    inform_server(loc_str, "00000000")
                    GPIO.output(FLASHLIGHT_PIN, False)
            #if time.perf_counter() >= timeToCheckAgvState: #as long as tag is present the time check runs ahead and condition not reached
            #    if agvState != AgvState.UNEQUIPPED_ELECTRIC: #this just to know when to stop playing local
            #        agvState = AgvState.UNEQUIPPED_ELECTRIC
            #        agv_str = getAgvStateStr("8878787")
            #        inform_server(agv_str, "8878787")
            if GPIO.input(LITTLE_AGV_ATTACHED_PIN) == True:
                smallAgvAttached = False
                time.sleep(1)
            if (GPIO.input(LITTLE_AGV_ATTACHED_PIN) == False) and (smallAgvAttached == False): #high jump recognized
                setNeopixelInitOn()
                time.sleep(1)
                station = initializeStationReader()
                stock1 = initializeStock1Reader()
                stock2 = initializeStock2Reader()
                smallAgvAttached = True
                print('Waiting for RFID/NFC card...')
                setNeopixelOff()

            # Check if a card is available to read
            if station is not None:
               stationTag = station.read_passive_target(timeout=0.1)
               if stationTag is not None:
                  #continue
                  if stationNotDetected == True:
                     setNeopixelOff()
                     stationNotDetected = False
                  timeToCheckLocState = time.perf_counter() + STATE_TRANSITION_INTERVAL
                  GPIO.output(FLASHLIGHT_PIN, True)
                  stationTag_str = get_uid_string(stationTag)
                  #print('Found station with nfc UID: ', stationTag_str)
                  if (location != getAgvLocation(stationTag_str)):
                     location = getAgvLocation(stationTag_str)
                     loc_str = getAgvLocation(stationTag_str)
                     inform_server(loc_str, agvState) #to local server  
            else:
               stationNotDetected = True 
            if smallAgvAttached == True:
                if (stock1 is not None) and (stock2 is not None): #NFC reader present
                    stock1Tag = stock1.read_passive_target(timeout=1.0)
                    stock2Tag = stock2.read_passive_target(timeout=1.0)
                    #if stock1Tag is not None:
                    #    print('Found stock1 with nfc UID: ', get_uid_string(stock1Tag))
                    #else:
                    #    print('no 1')
                    #if stock2Tag is not None:
                    #    print('Found stock2 with nfc UID: ', get_uid_string(stock2Tag))
                    #else:
                    #    print('no 2')
                    stock1TagStr = "00000000"
                    stock2TagStr = "00000000"
                    if stock1Tag is not None:
                       stock1TagStr = get_uid_string(stock1Tag)
                       #timeToCheckAgvState = time.perf_counter() + STATE_TRANSITION_INTERVAL
                    if stock2Tag is not None:
                       stock2TagStr = get_uid_string(stock2Tag)
                       #timeToCheckAgvState = time.perf_counter() + STATE_TRANSITION_INTERVAL
                    if (agvState != (getAgvState(stock1TagStr, stock2TagStr))):
                        tagTransitionCount += 1
                        if tagTransitionCount >= MIN_NO_OF_SAME_TAGE_BEFORE_TRANSITION:
                           agvState = getAgvState(get_uid_string(stock1Tag), get_uid_string(stock2Tag))  
                           print(agvState)
                           publishNextAgvState(agvState)
                           inform_server(location, agvState) #localServer
                           tagTransitionCount = 0
            #neopixel handling
            if time.perf_counter() > timeToSwitchNeopixel:
               littleAgvFull = False
               #print(agvState)
               if agvState == AgvState.EQUIPPED_ELECTRIC_PART2 or agvState == AgvState.EQUIPPED_HYBRID_PART2:
                  littleAgvFull = True
               if stationNotDetected == True:
                  setNeopixelRedOn()
                  if smallAgvAttached == True:
                     time.sleep(3)
                     os.system('reboot')
                     #initializeStationReader()
               elif agvState == AgvState.WRONG_PART:
                  setNeopixel(RED) #fail
               elif smallAgvAttached == False and location == getAgvLocation("00000000"): #not on station without little agv
                  #setNeopixel(WAITING1) #blue
                  setNeopixel(UNDEFINED) #white blink
               elif smallAgvAttached == True and location == getAgvLocation("00000000"): #not on station without little agv
                  #setNeopixel(UNDEFINED) #white
                  setNeopixelWhiteOn()
               elif smallAgvAttached == False and location != getAgvLocation("00000000"): #on station without little agv
                  setNeopixel(WAITING2) #green blinking
               elif smallAgvAttached == True and location != getAgvLocation("00000000") and littleAgvFull == False: #on station with little agv and not full
                  #setNeopixel(PROGRESS) #orange
                  setNeopixelGreenOn()
               elif agvState == AgvState.EQUIPPED_ELECTRIC_PART1:
                  setNeopixel(TRANSMIT) #violet blinking
               elif littleAgvFull == True:
                  setNeopixelPurpleOn() #violet
               timeToSwitchNeopixel = time.perf_counter() + 1.0

    except Exception as e:
        print(e)
        inform_server("error: " + str(e), agvState) #does it make sense here?
        pass
        #goto .begin
    finally:
        #GPIO.cleanup()
        pass

