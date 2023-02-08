//Library for LEDs, DHT11 sensor and Bluetooth
#include <PololuLedStrip.h>
#include <SimpleDHT.h>
#include <SoftwareSerial.h>

//Create a Led ribbon object and specify which pin controls it (here pin 12)
PololuLedStrip<12> ledStrip; 
#define LED_COUNT 7
rgb_color colors[LED_COUNT];

//Bluetooth Sensor 
SoftwareSerial Bluetooth(11, 10); // RX, TX
int pinBluetooth_rx = 11;
int pinBluetooth_tx =10;
int command;

//DHT11 Sensor
int pinDHT11 = 6;
SimpleDHT11 dht11;
int err = SimpleDHTErrSuccess;

//CO2 Sensor 
int percentage;
float volts;
int LEDALERTE = 2;

//We define the constants for the CO2 sensor 
#define         MG_PIN                       (A0)    //define which analog input channel you are going to use
#define         BOOL_PIN                     (2)
#define         DC_GAIN                      (8.5)   //define the DC gain of amplifier
#define         READ_SAMPLE_INTERVAL         (50)    //define how many samples you are going to take in normal operation
#define         READ_SAMPLE_TIMES            (5)     //define the time interval(in milisecond) between each samples in
                                                     //normal operation
#define         ZERO_POINT_VOLTAGE           (0.300) //define the output of the sensor in volts when the concentration of CO2 is 400PPM
#define         REACTION_VOLTGAE             (0.030) //define the voltage drop of the sensor when move the sensor from air into 1000ppm CO2

/*****************************Globals***********************************************/
float           CO2Curve[3]  =  {2.602,ZERO_POINT_VOLTAGE,(REACTION_VOLTGAE/(2.602-3))};
                                                     //two points are taken from the curve.
                                                     //with these two points, a line is formed which is
                                                     //"approximately equivalent" to the original curve.
                                                     //data format:{ x, y, slope}; point1: (lg400, 0.324), point2: (lg4000, 0.280)
                                                     //slope = ( reaction voltage ) / (log400 –log1000)
                                                     
void setup() {
  //Initialisation of the serial port Bluetooth
  pinMode(pinBluetooth_rx, INPUT);
  pinMode(pinBluetooth_tx, OUTPUT);
  Bluetooth.begin(9600);

  //DHT11 sensor initialization
  pinMode(pinDHT11, INPUT_PULLUP);
  Serial.begin(9600);
  Serial.println("Attente du caractère 'm' pour afficher les données");

  //CO2 sensor initialisation  
  pinMode(BOOL_PIN, INPUT);                        //set pin to input
  digitalWrite(BOOL_PIN, HIGH);
  pinMode(LEDALERTE, OUTPUT);
}

void loop() {
  Serial.println(CO2value());
  if (CO2value()>1250){
   setLEDcolor(100,0,0);
  }
  else {
    setLEDcolor(0,100,0);
  }
  // when characters arrive over the serial port...
  if (Bluetooth.available()) {
    command = Bluetooth.read();
    if ( command == 0 ) {
      getTemperatureandCO2();//Temperature and CO2 sensor reading
    } else {
      Serial.println(command);
    }
  }
}

/*****************************  getTemperatureandCO2 **********************************
Input:  Nothing in input
Output:  Returns via the bluetooth sensor the data from the DHT11 and CO2 sensors in the format "temperature (in °C), humidity (%), CO2 (ppm)"
Remarks: This function sends the data from the DHT11 and CO2 sensors via the Bluetooth sensor
************************************************************************************/
void getTemperatureandCO2() {
  byte temperature = 0;
  byte humidity = 0;
  
  if ((err = dht11.read(pinDHT11, &temperature, &humidity, NULL)) != SimpleDHTErrSuccess) {
    //If we can't read the data:
    Serial.print("Read DHT11 failed, err="); Serial.println(err); delay(1000);
    return;
  }
  /*
  Serial.print((int)temperature);
  Serial.print("°C, ");
  Serial.print((int)humidity);
  Serial.println("%");
  */
  Bluetooth.print((int)temperature);
  Bluetooth.print(",");
  Bluetooth.print((int)humidity);
  Bluetooth.print( "," );
  
  // Variable pour les mesures de CO2
  percentage = CO2value();
    if (percentage == -1) {
        Bluetooth.println(400);
        //Serial.println(400);
    } else {
        Bluetooth.println(percentage);
        //Serial.println(percentage);
    }
}

/*****************************  CO2value *********************************************
Input:  Nothing
Output:  output of the consentration of CO2 
Remarks: This function reads the CO2 concentration and return it
************************************************************************************/
int CO2value(){
  volts = MGRead(MG_PIN);
  return  MGGetPercentage(volts,CO2Curve);
}


/*****************************  MGRead *********************************************
Input:   mg_pin - analog channel
Output:  output of SEN-000007
Remarks: This function reads the output of SEN-000007
************************************************************************************/
float MGRead(int mg_pin){
    int i;
    float v=0;

    for (i=0;i<READ_SAMPLE_TIMES;i++) {
        v += analogRead(mg_pin);
        delay(READ_SAMPLE_INTERVAL);
    }
    v = (v/READ_SAMPLE_TIMES) *5/1024 ;
    return v;
}

/*****************************  MQGetPercentage **********************************
Input:   volts   - SEN-000007 output measured in volts
         pcurve  - pointer to the curve of the target gas
Output:  ppm of the target gas
Remarks: By using the slope and a point of the line. The x(logarithmic value of ppm)
         of the line could be derived if y(MG-811 output) is provided. As it is a
         logarithmic coordinate, power of 10 is used to convert the result to non-logarithmic
         value.
************************************************************************************/
int  MGGetPercentage(float volts, float *pcurve)
{
   if ((volts/DC_GAIN )>=ZERO_POINT_VOLTAGE) {
      return -1;
   } else {
      return pow(10, ((volts/DC_GAIN)-pcurve[1])/pcurve[2]+pcurve[0]);
   }
}

void setLEDcolor(int red, int green, int blue){
  rgb_color color;
   color.red = red;
   color.green = green;
   color.blue = blue;
    // Update the colors buffer
    for(uint16_t i = 0; i < LED_COUNT; i++)
    {
      colors[i] = color;
    }
    // Write to the LED strip
    ledStrip.write(colors, LED_COUNT);
}