/* CODE EXPLAIN
create by Adrian Zajączkowski

Inspiration to create checksum --> https://docs.m2stud.io/ee/arduino/4-Serial-Communication/

Meansure rising egde of incoming signals. 
Algorithm:
1. Detect rising/faling egde 
2. save value of timer ( in ICP mode ) to variable no.1
3. detect second egde and save value of timer to variable no.2
4. compare two variables:
4.1 if variable 1>varialbe 2 ---> (variable2-variable1) add max value of timer for overflow 
4.2 else ---> (variable2-variable1)
5. count check sum with XOR from value from point 4.
6. send data to PC with cover ( start,value,checsum,stop)
7. repeat

*/
#include <Arduino.h>
#define icpPin 49               // number of IPC pin in Arduino Mega for timer 4 
volatile long Overflow;  
// bool shouldISpam = false;    // flag to asynchronymous sending data
volatile uint16_t Nprev = 0;    // storage previous value of timer ( variable 1)
volatile uint16_t Nnext = 0;    // second value of timer (variable 2)
volatile uint16_t ovf = 65535;  // max count of 16-bit timer 4

struct Data
{                               // struct to hold difference
  uint16_t Nx;                  // difference, why uint16_t? timer is 16-bit if we use ICR4, 
};                              // uint8_t if we use ICR4L and ICR4H <--- read in docs  

struct Packet
{
                                // package to send to PC
  uint16_t start_seq;           // 0x0210, 0x10 <- two start variable as flag 
  uint8_t len;                  // length of payload
  struct Data Nx_data;
  uint8_t checksum;             
  uint16_t end_seq;             // 0x0310, 0x10 <- two end variable as flag 
 
};

struct Packet send_packed; 

uint8_t calc_checksum(void *data, uint8_t len)  // function to count checksum
{
  uint8_t checksum = 0;
  uint8_t *tmp;
  for(tmp = (uint8_t*)data; tmp < (data + len); tmp++){
                                                // xor all the bytes
    checksum ^= *tmp;                           // checksum = checksum xor value stored in tmp
  }
  return checksum;
}

void send_packet(){                             // function to send ready package via serial
  send_packed.len = sizeof(struct Data);        
  send_packed.checksum = calc_checksum(&send_packed.tx_data, send_packed.len);  // count checksum of actually data
  Serial.write((char*)&send_packed, sizeof(send_packed));                       // send data via serial as package of characters, length of packet
}
void setup()
{ 
  Serial.begin(115200);
  send_packed.start_seq = 0x0210;               // configuration of start end end sequence
  send_packed.end_seq = 0x0310;
  
 pinMode(icpPin, INPUT);                        

  noInterrupts ();                              // disable interrupts to secure code

  TCCR4A = 0;                                   // configuration registers of timer 4, more information on page 133( 17 of timers) in docs
  TCCR4B = 0;
  TCNT4 = 0;
  TIMSK4 = 0;

  TCCR4B |= _BV(ICNC4)| _BV(ICES4) |_BV(CS40);  // noise canceler /rising egde/ prescaler (1)
  TIFR4 |= _BV(ICF4) |  _BV(TOV4);              // ICP and overflow flag
  TIMSK4 |= _BV(ICIE4) | _BV(TOIE4);            // ICP and overflow enable

  interrupts ();                                // enable interrupts
}

ISR(TIMER4_OVF_vect){                           // function to overflows 
	Overflow++;
}

ISR(TIMER4_CAPT_vect)                           // function to capture event 
{
    if (bitRead(TCCR4B,ICES4))                  // if detect rising/falling egde
    {
        Nnext = ICR4;                           // ICR4 <-- value of timer while event occuret
        if(Nnext>Nprev){                         
          send_packed.Nx_data.Nx=ICR4-Nprev;    // save difference to package to send
          Nprev = ICR4;
        }else{
          send_packed.Nx_data.Nx = ICR4-Nprev+65535;  
          Nprev = ICR4;
        }
      }

}
void loop()                                     // infinite loop
{ 
    send_packet();                              // sending data 
}
