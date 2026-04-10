#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>

#define TFT_CS 10
#define TFT_DC 7
#define TFT_RST 8
#define TFT_BL 9

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

#define CMD_INIT 'I'
#define CMD_CLEAR 'C'
#define CMD_RECT 'R'
#define CMD_CIRCLE 'O'
#define CMD_TRIANGLE 'G'
#define CMD_WIRE 'W'
#define CMD_TEXT 'T'
#define CMD_READ 'D'
#define CMD_WRITE 'L'
#define CMD_WIN 'V'
#define CMD_ANALOG_READ 'a'   
#define CMD_ANALOG_WRITE 'A'  

void setup() {
  pinMode(16, INPUT); 
  pinMode(17, INPUT);
  Serial.begin(115200);
  tft.init(240, 320, SPI_MODE3);
  tft.setRotation(0);
  tft.fillScreen(ST77XX_BLACK);
  pinMode(TFT_BL, OUTPUT);
  digitalWrite(TFT_BL, HIGH);
  delay(100);
  //Serial.write('K');
}

uint16_t getColor(uint8_t code) {
  switch (code) {
    case 0: return ST77XX_WHITE;
    case 1: return ST77XX_RED;
    case 2: return ST77XX_GREEN;
    case 3: return ST77XX_BLUE;
    case 4: return ST77XX_YELLOW;
    case 10: return ST77XX_BLACK;
    case 5: return 0x7BEF; // GREY
    default: return ST77XX_WHITE;
  }
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    switch (cmd) {
      case CMD_INIT:
        while (Serial.available() < 4);
        {
          int16_t w = Serial.read() | (Serial.read() << 8);
          int16_t h = Serial.read() | (Serial.read() << 8);
          tft.init(w, h, SPI_MODE3);
          tft.fillScreen(ST77XX_BLACK);
          Serial.write('K');
        }
        break;

      case CMD_CLEAR:
        tft.fillScreen(ST77XX_BLACK);
        Serial.write('K');
        break;

      case CMD_RECT:
      case CMD_WIRE:
        while (Serial.available() < 9);
        {
          int16_t x = Serial.read() | (Serial.read() << 8);
          int16_t y = Serial.read() | (Serial.read() << 8);
          int16_t w = Serial.read() | (Serial.read() << 8);
          int16_t h = Serial.read() | (Serial.read() << 8);
          uint8_t colorCode = Serial.read();
          tft.fillRect(x, y, w, h, getColor(colorCode));
          Serial.write('K');
        }
        break;

      case CMD_CIRCLE:
        while (Serial.available() < 7);
        {
          int16_t x = Serial.read() | (Serial.read() << 8);
          int16_t y = Serial.read() | (Serial.read() << 8);
          int16_t r = Serial.read() | (Serial.read() << 8);
          uint8_t colorCode = Serial.read();
          tft.fillCircle(x, y, r, getColor(colorCode));
          Serial.write('K');
        }
        break;

      case CMD_TRIANGLE:
        while (Serial.available() < 13);
        {
          int16_t x0 = Serial.read() | (Serial.read() << 8);
          int16_t y0 = Serial.read() | (Serial.read() << 8);
          int16_t x1 = Serial.read() | (Serial.read() << 8);
          int16_t y1 = Serial.read() | (Serial.read() << 8);
          int16_t x2 = Serial.read() | (Serial.read() << 8);
          int16_t y2 = Serial.read() | (Serial.read() << 8);
          uint8_t colorCode = Serial.read();
          tft.fillTriangle(x0, y0, x1, y1, x2, y2, getColor(colorCode));
          Serial.write('K');
        }
        break;

      case CMD_TEXT:
        while (Serial.available() < 6);
        {
          int16_t x = Serial.read() | (Serial.read() << 8);
          int16_t y = Serial.read() | (Serial.read() << 8);
          uint8_t size = Serial.read();
          uint8_t colorCode = Serial.read();
          uint8_t len = Serial.read();
          char buffer[64] = {0};
          for (int i = 0; i < len; i++) {
            while (!Serial.available());
            buffer[i] = (char)Serial.read();
          }
          tft.setCursor(x, y);
          tft.setTextColor(getColor(colorCode));
          tft.setTextSize(size);
          tft.print(buffer);
          Serial.write('K');
        }
        break;

      case CMD_READ:
        {
          while (Serial.available() < 1);
          uint8_t pin = Serial.read();
          // Explicitly set pin mode before reading
          pinMode(pin, INPUT);
          Serial.write(digitalRead(pin));
        }
        break;

      case CMD_WRITE:
        {
          while (Serial.available() < 2);
          uint8_t pin = Serial.read();
          uint8_t state = Serial.read();
          pinMode(pin, OUTPUT);
          digitalWrite(pin, state);
          Serial.write('K');
        }
        break;

      // case CMD_WIN:
      //   {
      //     pinMode(16, OUTPUT);
      //     digitalWrite(16, HIGH);
      //     pinMode(17, INPUT);
      //     pinMode(13, OUTPUT);
      //     digitalWrite(13, HIGH);
      //     Serial.write('K');
      //   }
      //   break;

      // case CMD_ANALOG_READ:
      //   {
      //     while (Serial.available() < 1);
      //     uint8_t pin = Serial.read();
      //     pinMode(pin, INPUT); // Ensure it is an input for reading
      //     int val = analogRead(pin); 
      //     Serial.write(lowByte(val));
      //     Serial.write(highByte(val));
      //   }
      //   break;

      // case CMD_ANALOG_WRITE:
      //   {
      //     while (Serial.available() < 3);
      //     uint8_t pin = Serial.read();
      //     int val = Serial.read() | (Serial.read() << 8);
          
      //     pinMode(pin, OUTPUT);
      //     // Check if the pin supports PWM. If not (Pins 16/17), use Digital
      //     if (pin == 16 || pin == 17) {
      //       digitalWrite(pin, (val >= 1000) ? HIGH : LOW);
      //     } else {
      //       analogWrite(pin, map(val, 0, 1000, 0, 255));
      //     }
      //     Serial.write('K');
      //   }
      //   break;
    }
  }
}