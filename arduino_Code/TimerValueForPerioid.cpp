/* CODE EXPLAIN

Timer count at first rising egde to another, and give to us perioid between two rising egdes. 
*/
#include <Arduino.h>
#define icpPin 49
volatile long Overflow;

void setup()
{
  Serial.begin(115200);

  pinMode(icpPin, INPUT);

  noInterrupts ();  // protected code
  // reset Timer 4
  TCCR4A = 0;
  TCCR4B = 0;
  TCNT4 = 0;
  TIMSK4 = 0;

  TIFR4 |= _BV(ICF4); // clear Input Capture Flag so we don't get a bogus interrupt
  TIFR4 |= _BV(TOV4); // clear Overflow Flag so we don't get a bogus interrupt

  TCCR4B = _BV(CS40) |// start Timer 4, no prescaler
		   _BV(ICES4)| // Input Capture Edge Select (4=Rising, 0=Falling)
		   _BV(ICNC4);
		   
  TIMSK4 |= _BV(ICIE4); // Enable Timer 4 Input Capture Interrupt
  TIMSK4 |= _BV(TOIE4); // Enable Timer 1 Overflow Interrupt
  interrupts ();
}

volatile unsigned int Tickmeansure = 0;


ISR(TIMER4_OVF_vect){
	Overflow++;
}
ISR(TIMER4_CAPT_vect)
{
    if (bitRead(TCCR4B,ICES4))
    {
        Tickmeansure = (1<<16)| TCNT4;
        TCNT4 = 0;      
        
      }
}
  
void loop()
{
  noInterrupts();
  uint32_t ticks = Tickmeansure;
  interrupts();

  // If a sample has been measured
  if (ticks)
  {
  
    Serial.println(ticks);

    noInterrupts();
    Tickmeansure = 0;
    interrupts();
  }
}