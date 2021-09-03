
from ev3dev2.led import Leds
from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, MoveTank, SpeedPercent
from ev3dev2.sound import Sound
from ev3dev2.button import Button
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor, TouchSensor
from ev3dev2._platform.ev3 import INPUT_1, INPUT_2
from time import sleep
from threading import Thread

ts = TouchSensor(INPUT_1, INPUT_2)
us = UltrasonicSensor()
cs = ColorSensor()
leds = Leds()
sound = Sound()
drive = MoveTank(OUTPUT_B, OUTPUT_C)
mLeft = LargeMotor(OUTPUT_B)
mRight = LargeMotor(OUTPUT_C)
dist = us.distance_centimeters
direction = "north"
count = 0
array_correction = []
# array_cli = []
number_calls = "Number of calls to reach a square: "

def correction():
    if (cs.reflected_light_intensity < 15):
        return

    sleep(1)
    drive.on_for_rotations(SpeedPercent(-15), SpeedPercent(-15), 1)

    if(cs.reflected_light_intensity < 15):
        drive.on(5, 5)
    sleep(0.5)

    while(cs.reflected_light_intensity > 15):
        angle = 30
        if(check_left(angle) == False):
            drive.on_for_rotations(SpeedPercent(-15), SpeedPercent(-15), 1)
            sleep(0.5)
            drive.on_for_degrees(0, SpeedPercent(-5), angle)
            sleep(0.5)
            check_right(angle)
        angle += 5
    if(cs.reflected_light_intensity < 15):
        return

def check_left(angle):
    drive.on_for_degrees(0, SpeedPercent(5), angle)
    sleep(0.5)
    drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), 1.1)

    if(cs.reflected_light_intensity < 15):
        return True
    else:
        return False

def check_right(angle):

    drive.on_for_degrees(SpeedPercent(5), 0, angle)
    sleep(0.5)

    drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), 1.1)

    if(cs.reflected_light_intensity < 15):
        return True
    else:
        drive.on_for_rotations(SpeedPercent(-15), SpeedPercent(-15), 1)
        drive.on_for_degrees(SpeedPercent(-5), 0, angle)
        return False

# def average_cli_reading():
#     # an array of black tile cli readings to calculate the average so we can keep away from possible outliers
#     array_cli.append(cs.reflected_light_intensity)
#     average = sum(array_cli) / len(array_cli)
#     return average


def turnRight():
    global direction
    drive.on_for_rotations(50, -55, 0.535, brake=True, block=True)
    if direction == "north":
        direction = "east"
    elif direction == "east":
        direction = "south"
    elif direction == "south":
        direction = "west"
    else:
        direction = "north"


def turnLeft():
    global direction
    drive.on_for_rotations(-50, 50, 0.535, brake=True, block=True)
    if direction == "north":
        direction = "west"
    elif direction == "east":
        direction = "north"
    elif direction == "south":
        direction = "east"
    else:
        direction = "south"


def findNextBlack():
    global count
    correction_counter = 0
    if cs.reflected_light_intensity > 15:
        while cs.reflected_light_intensity > 15:
            drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), 1)
            correction_counter += 1
            correction()
        drive.stop()
        if(cs.reflected_light_intensity < 15):
            array_correction.append(correction_counter)
            while (cs.reflected_light_intensity < 15):
                drive.on(20, 20)
            drive.stop()

        if direction == "east":
            count += 1
        elif direction == "south":
            count += 15

        print(count)
        print(number_calls, correction_counter)
        sound.beep()
        return
    else:
        while (cs.reflected_light_intensity) < 15:
            drive.on(10, 10)
        drive.stop()
        findNextBlack()


def sensors():
    while us.distance_centimeters > 250:
        drive.on_for_rotations(SpeedPercent(50), SpeedPercent(50), 1.6)
        sleep(2)
        turnLeft()
        drive.on_for_rotations(SpeedPercent(50), SpeedPercent(50), 1.6)
        sleep(2)
        turnRight()
    if not ts.is_pressed:
        drive.on(left_speed=50, right_speed=50)
    elif ts.is_pressed:
        drive.off()
        sound.beep()
        return
    sensors()


def initialize():
    drive.on_for_rotations(SpeedPercent(50), SpeedPercent(50), 1)
    sleep(1)
    turnRight()
    sleep(1)
    drive.on_for_rotations(SpeedPercent(50), SpeedPercent(50), 15.6)
    sleep(1)
    turnRight()
    sleep(1)
    drive.on_for_rotations(SpeedPercent(50), SpeedPercent(50), 6.8)
    sleep(1)


# initialize()
# sensors()

drive.on_for_rotations(SpeedPercent(50), SpeedPercent(50), 1)
sleep(1)
turnRight()
sleep(1)
while count < 16:
    findNextBlack()
