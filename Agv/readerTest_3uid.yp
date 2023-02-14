"""
This example shows connecting to the PN532 with I2C (requires clock
stretching support), SPI, or UART. SPI is best, it uses the most pins but
is the most reliable and universally supported.
After initialization, try waving various 13.56MHz RFID cards over it!
"""

import RPi.GPIO as GPIO

import pn532.pn532 as nfc
from pn532 import *
#from goto import with_goto
block_number = 6
key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
data = bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F])

def get_uid_string(uid):
    uid_str = ''
    for i in uid:
        hex_str = str(hex(i))
        uid_str = uid_str + hex_str[2:]
    return uid_str



if __name__ == '__main__':
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        pn532_23 = PN532_SPI(debug=False, reset=20, cs=23)
        pn532_24 = PN532_SPI(debug=False, reset=20, cs=24)
        #pn532 = PN532_I2C(debug=False, reset=20, req=16)
        #pn532 = PN532_UART(debug=False, reset=20)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        ic23, ver23, rev23, support23 = pn532_23.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver23, rev23))
        # Configure PN532 to communicate with MiFare cards
        pn532_23.SAM_configuration()

        ic24, ver24, rev24, support24 = pn532_24.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver24, rev24))
        # Configure PN532 to communicate with MiFare cards
        pn532_24.SAM_configuration()

        print('Waiting for RFID/NFC card...')
        #label .begin
        while True:
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=0.1)
            #print('.1', end="")
            # Try again if no card is available.
            if uid is not None:
                #continue
                print('Found card with UID:', [hex(i) for i in uid], 'as string: ', get_uid_string(uid))
                #block_number = 6
                #data = bytes([0x00, 0x01, 0x02, 0x03])
                #try:
                #   print('after try')
                #   pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
                #   print('after auth')
                #   pn532.mifare_classic_write_block(block_number, data)
                #   if pn532.mifare_classic_read_block(block_number) == data:
                #      print('write block %d successfully' % block_number)
                #   print('after if')
                #except nfc.PN532Error as e:
                #   print(e.errmsg)

            uid23 = pn532_23.read_passive_target(timeout=0.1)
            #print('.2', end="")
            if uid23 is not None:
                #continue
                print('Found card with UID_23:', [hex(i) for i in uid23], 'as string: ', get_uid_string(uid23))

            uid24 = pn532_24.read_passive_target(timeout=0.1)
            #print('.3', end="")
            if uid24 is not None:
                #continue
                print('Found card with UID_24:', [hex(i) for i in uid24], 'as string: ', get_uid_string(uid24))


    except Exception as e:
        print(e)
        pass
        #goto .begin
    finally:
        GPIO.cleanup()
