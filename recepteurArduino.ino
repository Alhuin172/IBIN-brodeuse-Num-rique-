#include <AccelStepper.h>  // Pour ceux du type du DM56 sinon il faut utiliser Stepper.h

#define fcx 2
#define fcy 3

#define STEP_PINY 4
#define DIR_PINY 5

#define STEP_PINZ 6
#define DIR_PINZ 7

#define STEP_PINX 8
#define DIR_PINX 9

#define Capt 10




const int nbpas = 1600;
const float rayonPoulieX = 6.36;
const float rayonPoulieY = 6.36;

int posx = 0;
int posy = 0;
volatile int buteX=0;
volatile int buteY=0;
struct Point {
  float x;
  float y;
};
Point p;

// Création de l’objet stepper en mode DRIVER (STEP/DIR)
AccelStepper stepperx(AccelStepper::DRIVER, STEP_PINX, DIR_PINX);
AccelStepper steppery(AccelStepper::DRIVER, STEP_PINY, DIR_PINY);
AccelStepper stepperz(AccelStepper::DRIVER, STEP_PINZ, DIR_PINZ);




void setup() {

  pinMode(Capt, INPUT);
  pinMode(fcx, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(fcx), stopx, RISING);
  pinMode(fcy, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(fcy), stopy, RISING);
  Serial.begin(115200);
  Serial.setTimeout(2);

  stepperx.setMaxSpeed(20000);     // Vitesse max en pas/s
  stepperx.setAcceleration(20000);  // Accélération en pas/s²

  steppery.setMaxSpeed(20000);     // Vitesse max en pas/s
  steppery.setAcceleration(2000);  // Accélération en pas/s²

  stepperz.setMaxSpeed(50000);      // Vitesse max en pas/s
  stepperz.setAcceleration(200000);  // Accélération en pas/s²

  // initialisationAxeZ();
  // initialisationAxeY();
  // initialisationAxeX();

}

void loop() {
  //Serial.println("loop");
  if (Serial.available() >= sizeof(Point)) {
    Serial.readBytes((char*)&p, sizeof(Point));
    //Serial.println(p.x);
    if (p.x==-150.0){
      initialisationAxeZ();
      initialisationAxeY();
      initialisationAxeX();
    }
    else if (p.x==-172.0)
    {
      Serial.print(posx);
      Serial.print(" ");
      Serial.println(posy);
    }
    else
    {
      //Serial.println("demande de deplacement"); 
      deplacement(p.x, p.y);
      //deplacement(10.2,10.2);  //déplacement du plateau
      //delay(2000);


      stepperz.move(800);

      while ((stepperz.distanceToGo() != 0) && (buteX == 0 && buteY == 0)) 
      {
        stepperz.run();
      }
        Serial.println("OK");
          // confirmation vers Python
    }
    }
}

void deplacement(float x, float y) {
  int px = x / (2 * 3.1415 * rayonPoulieX) * nbpas - posx;
  int py = y / (2 * 3.1415 * rayonPoulieY) * nbpas - posy;
  stepperx.move(px);
  steppery.move(py);
  posx += px;
  posy += py;
  
  while ((stepperx.distanceToGo() != 0 || steppery.distanceToGo() != 0) 
       && (buteX == 0 && buteY == 0)) {
      //Serial.println("deplacement");
    stepperx.run();
    steppery.run();
  }
}
void stopx() {
  buteX=1;
   /*
  Serial.println("SR X");
  if (ini==1) {
     stepperx.move(10);
  while (stepperx.distanceToGo() != 0) {
    stepperx.run();
  }
  }
  else {
  stepperx.setMaxSpeed(0);     // Vitesse max en pas/s
  stepperx.setAcceleration(0);  // Accélération en pas/s²

  } */
}

void stopy() {
  buteY=1;
 /* Serial.println("SR Y");
  if (ini==1) {
     steppery.move(10);
  while (steppery.distanceToGo() != 0) {
    steppery.run();
  }
  }
  else {
  steppery.setMaxSpeed(0);     // Vitesse max en pas/s
  steppery.setAcceleration(0);  // Accélération en pas/s²

  } */
}

void initialisationAxeX()
{
  Serial.println("debut initialisation axe x");
  delay(100);
  while(buteX==0){
    stepperx.move(-1);
    while (stepperx.distanceToGo() != 0 && buteX==0){stepperx.run();
    }
  }
  delay(10);//important de le laisser

  stepperx.move(40);
  while (stepperx.distanceToGo() != 0) {
    stepperx.run();
  }
  buteX=0;
  Serial.println("axe X initialise");

}
void initialisationAxeY()
{
  Serial.print("debut initialisation axe Y");
  delay(100);
    while(buteY==0){
    steppery.move(-1);
    while (steppery.distanceToGo() != 0 && buteY==0 ){steppery.run();
    }
    }
  delay(1);//important de le laisser

  steppery.move(40);
  while (steppery.distanceToGo() != 0) {
    steppery.run();
  }
  Serial.println("axe Y initialise");
  buteY=0;
  

}
void initialisationAxeZ()
{
  Serial.print("debut initialisation axe Z");
  delay(100);
  while(digitalRead(Capt)){
    stepperz.move(1);
    while (stepperz.distanceToGo() != 0){stepperz.run();
    }
  }
  delay(10);//important de le laisser
  if (digitalRead(Capt))
  {
    Serial.println("on refait un tour");
    initialisationAxeZ();
  }
  Serial.println("axe Z initialise");
}