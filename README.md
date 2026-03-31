# ENGI1020-Bomb-Defused-Game

This is the code for our ENGI 1020 project for Engineering One at Memorial University. This project is heavily inspired by the game Keep Talking and Nobody Explodes, as this is an attempt to make the game in real life. This is the source code, 3D model, and wiring for our project, running on 2 Grove Beginner Arduino Kit.

## Description

This project is the final project for our ENGI 1020 course at Memorial University. In this project we are using 2 grove beginner kit to achieve all 6 modules: Morse Code, Simon Says, Passwords, Mazes, Wires, and the Timer module. for Morse Code, Simon Says, we only uses buzzer, LEDs, and buttons to make this module, but for the Passwords module, we used a I2C LCD, and 6 buttons to make it work. For the Timer module, we used a 4 pin clock segmented display to achieve the timer effect. For both Mazes and Wires, we are using 2 OLED screens with SPI connections to achieve the functionality of the module. Thus, we make a split between the modules, where all modules without an OLED screen will be runned on one of the Grove Kit, and other modules with an OLED will be runned on the other Grove Kit. Now, since there is no good firmware and driver for an OLED screen with SPI connection with grove kit, we went and made our own firmware, called SPI_ARDUINO.ino. then we upload this firmware onto the Grove Kit, afterwards, we also coded a library that works with this firmware, called LCDDriver, This is called an LCDDriver because OLED is technicalled an LCD, so we named it more broad, hoping to put more into this firmware later. We have also used the engi1020 firmware and library to make the other games, though we need to change and modify the firmware ourselves to make the timer module work, it is still mostly engi1020 firmware and library, thus we will acknowledge this later in the acknowledge section. All code, 3D model, and wiring diagrams are in this github, at different sections with corresponding folder names.

## Authors

Yicheng (Abner) Zhang
yichengz@mun.ca

Eric Guzzwell
ejguzzwell@mun.ca

## Donations

If you want to support us, please use link: https://buymeacoffee.com/yichengz

## Acknowledgments

* Keep Talking and Nobody Explodes
* Memorial University engi1020 firmware