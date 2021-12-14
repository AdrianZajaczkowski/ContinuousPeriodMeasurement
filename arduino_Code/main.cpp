#include <Arduino.h>

#include <CaptureTimer.h>

#define inputsignal  21 // pin odpowiedzialny za tryb input capture 2, 3, 18, 19, 20, 21
uint32_t ticks;
void setup() {
  Serial.begin(115200); 
                        
  CaptureTimer::initCapTime(inputsignal,RISING);
}


void loop() {
 

  if (CaptureTimer::getTickCapture(&ticks) == true)
  {
		Serial.write((byte*)&ticks,4);

    }
}