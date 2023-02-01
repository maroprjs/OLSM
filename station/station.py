import RPi.GPIO as GPIO
from pn532 import *
import socket

UDP_IP = "10.200.21.80"
UDP_PORT = 5555
MESSAGE = socket.gethostname()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def get_uid_string(uid):
    uid_str = ''
    for i in uid:
        hex_str = str(hex(i))
        uid_str = uid_str + hex_str[2:]
    return uid_str

def inform_server(nfc_tag):
   #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
   sock.sendto(bytes(MESSAGE + "," + nfc_tag , "utf-8"), (UDP_IP, UDP_PORT))
   #sock.close()
   #sock.shutdown(socket.SHUT_RDWR)

if __name__ == '__main__':
    #print($HOSTNAME)
    #print(socket.gethostname())
    try:
        pn532 = PN532_I2C(debug=False, reset=20, req=16)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()
        print('Waiting for RFID/NFC card...')
        while True:
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=1.5)
            print('.', end="")
            if uid is not None:
                uid_as_str = get_uid_string(uid)
                print('Found card with UID:', [hex(i) for i in uid], 'as string: ', uid_as_str)
                inform_server(uid_as_str)
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
