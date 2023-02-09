/**
 *  based on the emulate_tag_ndef example, found in https://github.com/elechouse/PN532
 *
 *  only uid nfc tag emulation is needed for one lot size manufactoring demo
 *
 *  connect pn532 in hsu mode to serial pins rx (D0), tx (D1) and raspberry pi (e.g. GPIO 17, 27, 22) to A0, A1 & A2
 *  additionally, pin D2 on arduino and built-in LED set to HIGH when nfc reader is detected
 *
 */
///////////////////////////////////////////////////////////////////////////////////////////////////
#include "Arduino.h"
#include "emulatetag.h"
#include "NdefMessage.h"
#include <SoftwareSerial.h>
#include <PN532_HSU.h>
#include <PN532.h>

///////////////////////////////////////////////////////////////////////////////////////////////////
//#define TEST_ON 1 //this is required to be disbaled when using arduinos with only one serial port
#define TAG_BIT1_PIN A0
#define TAG_BIT2_PIN A1
#define TAG_BIT3_PIN A2
#define NFC_DETECTED_PIN 2
#define UPDATE_INTERVAL 300 // [ms]

////////////////////////////////////////////////////////////////////////////////////////////////////
PN532_HSU pn532hsu(Serial); //PN532_HSU pn532hsu(Serial1); <-change thos for test with Arduino Mega
EmulateTag nfc(pn532hsu);
SoftwareSerial ss(11, 12); //rx,tx //serial to talk to raspberry
uint8_t gNdefBuf[120];
NdefMessage gMessage;
int gMessageSize;
uint8_t gUid[4] = { 0x10, 0x10, 0x11 };
uint8_t gUidLength = 3;
unsigned long gElapsedTime;

////////////////////////////////////////////////////////////////////////////////////////////////////
void fillUIDWordsWith(uint8_t filler){
	for (uint8_t i=0; i < gUidLength; i++)
	{
	  gUid[i] = filler;
	}
}

///////////////////////////////////////////////////////////////////////////////////////////////////
uint8_t isUIDChangeRequired(){
	uint8_t retVal = 0x00;
	  if ((digitalRead(TAG_BIT1_PIN) == LOW) && (digitalRead(TAG_BIT2_PIN) == LOW) && (digitalRead(TAG_BIT3_PIN) == LOW)) retVal = 0x10;
	  if ((digitalRead(TAG_BIT1_PIN) == HIGH) && (digitalRead(TAG_BIT2_PIN) == LOW) && (digitalRead(TAG_BIT3_PIN) == LOW)) retVal = 0x21;
	  if ((digitalRead(TAG_BIT1_PIN) == LOW) && (digitalRead(TAG_BIT2_PIN) == HIGH) && (digitalRead(TAG_BIT3_PIN) == LOW)) retVal = 0x32;
	  if ((digitalRead(TAG_BIT1_PIN) == HIGH) && (digitalRead(TAG_BIT2_PIN) == HIGH) && (digitalRead(TAG_BIT3_PIN) == LOW)) retVal = 0x43;

	  if ((digitalRead(TAG_BIT1_PIN) == LOW) && (digitalRead(TAG_BIT2_PIN) == LOW) && (digitalRead(TAG_BIT3_PIN) == HIGH)) retVal = 0x54;
	  if ((digitalRead(TAG_BIT1_PIN) == HIGH) && (digitalRead(TAG_BIT2_PIN) == LOW) && (digitalRead(TAG_BIT3_PIN) == HIGH)) retVal = 0x65;
	  if ((digitalRead(TAG_BIT1_PIN) == LOW) && (digitalRead(TAG_BIT2_PIN) == HIGH) && (digitalRead(TAG_BIT3_PIN) == HIGH)) retVal = 0x76;
	  if ((digitalRead(TAG_BIT1_PIN) == HIGH) && (digitalRead(TAG_BIT2_PIN) == HIGH) && (digitalRead(TAG_BIT3_PIN) == HIGH)) retVal = 0x87;
	  return retVal;
}

//////////////////////////////////////////////////////////////////////////////////////////////////
void handleCmdsFromSerial(){
    while (ss.available()){ //softserial doesn't work well with Raspberry
      char cmd = ss.read();
      //Serial.print("received ");Serial.println(cmd);
      ss.flush();
      if (cmd == '0') fillUIDWordsWith(0x10);
      if (cmd == '1') fillUIDWordsWith(0x21);
      if (cmd == '2') fillUIDWordsWith(0x32);
      if (cmd == '3') fillUIDWordsWith(0x43);
      if (cmd == '4') fillUIDWordsWith(0x54);
      if (cmd == '5') fillUIDWordsWith(0x65);
      if (cmd == '6') fillUIDWordsWith(0x76);
      if (cmd == '7') fillUIDWordsWith(0x87);
      if (cmd == '8') fillUIDWordsWith(0x98);
      if (cmd == '9') fillUIDWordsWith(0xA9);
      nfc.setUid(gUid);
      ss.println(cmd);

    }
}

///////////////////////////////////////////////////////////////////////////////////////////////////
void setup()
{

  #ifdef TEST_ON //therr is only one serial on arduino nano
	 Serial.begin(115200);
     Serial.println("------- Emulate Tag --------");
  #endif
  ss.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(NFC_DETECTED_PIN, OUTPUT);
  pinMode(TAG_BIT1_PIN, INPUT);
  pinMode(TAG_BIT2_PIN, INPUT);
  pinMode(TAG_BIT3_PIN, INPUT);

  gMessage = NdefMessage();
  gMessage.addUriRecord("http://www.nokia.com");
  gMessageSize = gMessage.getEncodedSize();
  if (gMessageSize > sizeof(gNdefBuf)) {
      #ifdef TEST_ON
         Serial.println("ndefBuf is too small");
      #endif
      while (1) { }
  };
  #ifdef TEST_ON
    Serial.print("Ndef encoded message size: ");
    Serial.println(gMessageSize);
  #endif

  gMessage.encode(gNdefBuf);

  // comment out this command for no ndef message
  nfc.setNdefFile(gNdefBuf, gMessageSize);

  // uid must be 3 bytes!
  nfc.setUid(gUid);
  nfc.init();
  gElapsedTime = millis();
}

//////////////////////////////////////////////////////////////////////////////////////////////////
void loop(){
    // uncomment for overriding ndef in case a write to this tag occured
    //nfc.setNdefFile(ndefBuf, messageSize);
	handleCmdsFromSerial();

    if (millis() >= gElapsedTime + UPDATE_INTERVAL){
    	uint8_t newUid = isUIDChangeRequired();
    	if (newUid != 0x00) fillUIDWordsWith(newUid);
    	gElapsedTime = millis();
    };

    // start emulation (blocks)
    //nfc.emulate(false);

    // or start emulation with timeout
    if(!nfc.emulate(1000)){ // timeout 1 second
        #ifdef TEST_ON
    	   Serial.print(".");
        #endif
    	digitalWrite(LED_BUILTIN, LOW);
    	digitalWrite(NFC_DETECTED_PIN, LOW);
    }else{
        #ifdef TEST_ON
    	   for (uint8_t i=0; i < uidLength; i++)
    	   {
    	     Serial.print(" 0x");Serial.print(uid[i], HEX);
    	   }
    	   Serial.println("");
        #endif
    	digitalWrite(LED_BUILTIN, HIGH);
    	digitalWrite(NFC_DETECTED_PIN, HIGH);
    }
    //delay(1000);
}
