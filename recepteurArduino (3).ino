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



bool axezinitialise=false;
const int nbpas = 1600;
const float rayonPoulieX = 6.36*4;
const float rayonPoulieY = 6.36;
const int distancelim = 15 ;

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
  stepperx.setAcceleration(40000);  // Accélération en pas/s²

  steppery.setMaxSpeed(20000);     // Vitesse max en pas/s
  steppery.setAcceleration(40000);  // Accélération en pas/s²

  stepperz.setMaxSpeed(50000);      // Vitesse max en pas/s
  stepperz.setAcceleration(100000);  // Accélération en pas/s²

}

void loop() {
  if (Serial.available() >= sizeof(Point)) {
    Serial.readBytes((char*)&p, sizeof(Point));
    if (p.x==-150.0){
      axezinitialise=false;
      initialisationAxeX();
      initialisationAxeY();
    }
    else if (p.x==-172.0)
    {
      Serial.print(posx);
      Serial.print(" ");
      Serial.println(posy);
    }
    else if (p.x==-179.0)
    {
      initialisationAxeZ();
      Serial.println("axe z initialisé");
      Serial.println("OK");
    }
     else if (p.x==-145.0)
    {
      initialisationAxeZ();
      Serial.println("axe z initialisé");
      Serial.println("OK");
    }
     else if (p.x==-25.0)
    {
      Serial.println("changement coordonné");
      Serial.println("OK");
      if (Serial.available() >= sizeof(Point)) {
      Serial.readBytes((char*)&p, sizeof(Point));
      posx=p.x;
      posy=p.y;
      Serial.println("les coordonnées initiales sont x=");
      Serial.print(posx);
      Serial.print(" et y=");
      Serial.print(posy);}
      Serial.println("OK");
    }
    else
    {
      deplacement(p.x, p.y);


      if (axezinitialise ) {
        stepperz.move(800);
        }
      else {initialisationAxeZ();}

      while ((stepperz.distanceToGo() != 0))// && (buteX == 0 && buteY == 0)) 
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
  stepperx.move(-px);
  steppery.move(py);
  posx += px;
  posy += py;
  if (pow(pow(px,2)+pow(py,2),1/2)>distancelim){
    stepperx.setMaxSpeed(4000);     // Vitesse max en pas/s lente
    stepperx.setAcceleration(8000);  // Accélération en pas/s²

    steppery.setMaxSpeed(4000);     // Vitesse max en pas/s lente
    steppery.setAcceleration(8000);  // Accélération en pas/s²

  }
  
  while ((stepperx.distanceToGo() != 0 || steppery.distanceToGo() != 0) 
       && (buteX == 0 && buteY == 0)) {
    stepperx.run();
    steppery.run();
  }
   stepperx.setMaxSpeed(40000);     // Vitesse max en pas/s
   stepperx.setAcceleration(80000);  // Accélération en pas/s²

   steppery.setMaxSpeed(40000);     // Vitesse max en pas/s
   steppery.setAcceleration(80000);  // Accélération en pas/s²

}
void stopx() {
  buteX=1;
  
}

void stopy() {
  buteY=1;
 
}

void initialisationAxeX()
{
  Serial.println("debut initialisation axe x");
  delay(100);
  while(buteX==0){
    stepperx.move(1);
    while (stepperx.distanceToGo() != 0 && buteX==0){stepperx.run();
    }
  }
  delay(10);//important de le laisser

  stepperx.move(-40);
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

  steppery.move(50);
  while (steppery.distanceToGo() != 0) {
    steppery.run();
  }
  Serial.println("axe Y initialise");
  buteY=0;
  

}
void initialisationAxeZ()
{
  int compt=0;
  Serial.println("debut initialisation axe Z");
  delay(100);
  while(digitalRead(Capt)){
    stepperz.move(1);
    compt++;
    while (stepperz.distanceToGo() != 0){stepperz.run();
    }
  }
  delay(10);//important de le laisser
  if (digitalRead(Capt))
  {
    Serial.println("on refait un tour");
    initialisationAxeZ();
  }
  axezinitialise=true;
  if (compt<400){
    stepperz.move(800);
  }
  else {
    stepperz.move(0);
  }
}