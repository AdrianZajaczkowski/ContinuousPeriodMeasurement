#include <Arduino.h>
#define SerialDiode 13
#define sendingDiode 10
volatile uint16_t overflowCount=0;
volatile uint16_t startseq;
volatile uint16_t endseq;
volatile uint16_t Nprev=0;
volatile uint16_t Nnext=0;
volatile uint16_t Tdiff=0;

struct __attribute__((packed)) Message {

  uint16_t start;  // znak początku paketu danych
  uint16_t Nx;     // obliczone Nx
  uint16_t end;    // znak końca pakietu
};

Message msg;       // tworzenie obiektu strutktury Message

void send_packet() {
  msg.start = startseq;
  msg.Nx = Tdiff; 
  msg.end = endseq;
  Serial.write((uint8_t *)&msg,sizeof(msg)); // wysyłanie danych do PC 

}

ISR (TIMER4_OVF_vect)             // przerwanie od przepełnień licznika 4 
{
  overflowCount++;
}  

ISR (TIMER4_CAPT_vect)            // przerwanie od przechwytywania zmiany stanu na pinie 
  {
        Nnext = ICR4;             // zapisanie wartości rejestru przechwytującego ICR4 jako zbocze Ni
        if(Nnext>Nprev){          // jeśli zbocze 2 jest większe od zbocza 1 
          Tdiff=(Nnext-Nprev);    // Wyznaczanie Nx
          Nprev = Nnext;          // zapis wartości ICR4 jako zbocze Ni-1
          overflowCount = 0;      // zerowanie ilości przepełnień 
        }else{
          Tdiff = ((Nnext-Nprev)+(overflowCount*65536)); // wyznaczenie Nx uwzględniając liczbę przepełnień 
          Nprev = Nnext;
          overflowCount = 0;
        }
  }  
  
void prepareForInterrupts ()
  {
  noInterrupts ();  // ochrona kodu przed nieprzewidzianym zakłóceniem 
  TCCR4A = 0;       // tryb normal
  TCCR4B = 0;   
  TIFR4 = bit (ICF4) | bit (TOV4);  // czyszczenie flagi przerwań i przepełnień
  TCNT4 = 0;                        // zerowanie licznika 4 
  overflowCount = 0;                // zerowanie ilości przepełnień
  TIMSK4 = bit (TOIE4) | bit (ICIE4);               // ustawienie flag przechwytywania i przepełnień
  TCCR4B =  bit (CS40) | bit (ICES4) | bit(ICNC4);  // startowanie licznika. Wykrywanie zbocza narastajacego, usunięcie zakłóceń, prescaler 1 
  interrupts ();
  }  
  

void setup () 
  {
  Serial.begin(38400);             // baudrate działające najoptymalniej w tym zadaniu    
  digitalWrite(SerialDiode,HIGH);  // Dioda sygnalizujaca działanie arduino
  prepareForInterrupts ();   

  } 

void loop () 
  {
    Tdiff = 90;
    if (Tdiff)                            // jeśli jest wartość Nx
    {                                    
      startseq = 0x02;                    // znak początku równy 2
      endseq = 0x03;                      // znak końca pakietu danych równy 3
      send_packet();                      // wysyłanie danych do PC
      digitalWrite(sendingDiode, HIGH);   // dioda sygnalizująca wysyłanie danych
    }else{
      digitalWrite(sendingDiode,LOW);
    }
}   
