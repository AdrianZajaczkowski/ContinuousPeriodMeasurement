/*

Modified by Adrian Zajączkowski
source to code example thus i modified: https://github.com/SMFSW/CaptureTimer/blob/master/examples/CaptureToAnalogic/CaptureToAnalogic.ino
copyright GNU Lesser General Public License v2.1


This code give to us frequency of incoming signal. 
When signal is ~ 1kHz - print 1
			   ~ 10kHz - print 10 and so one
if signal is less than 1kHz, program print 0 
Tested in changing frequency signal in range 10kHz - 100kHz in 10s time between this two value
*/
#include <Arduino.h>

#include <CaptureTimer.h>


#define samplingPer			0	//!< Acquisition period 

#define maxTicks			65536	//!< maximum ticks expected in an acquisition window


#define icINPin				2		//!< Pin used for Input Capture (ticks count)
// Literal Pin / Board
// 2 / most arduino boards (or D2)
// D4 / WeMos D1 R2
// #2 / Feather HUZZAH


/*** GLOBAL VARS ***/
uint16_t valOut = 0;


void setup()
{
	#if !defined(__TINY__)
		Serial.begin(115200);
	#endif
	
	CaptureTimer::initCapTicks(samplingPer, icINPin,RISING);
	

}

void loop()
{
	uint16_t ticks;
	
	
	if (CaptureTimer::getTicks(&ticks) == true)			// new data acquired (happens once every (samplingPer)ms)
	{
		ticks = min(ticks, maxTicks);					// clamp value against max expected
		Serial.println(ticks);							/// sprawdz
		//Serial.write((byte*)&ticks,4);
	}
}